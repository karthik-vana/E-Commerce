"""
src/services/chat_service.py
─────────────────────────────────────────────────────────────────────
Orchestrates the full request pipeline:
  UI -> ChatService -> PromptEngine -> GroqClient -> formatted response

Responsibilities
────────────────
• Input validation & sanitisation
• Relevance / safety guardrail check
• Prompt assembly
• API call delegation (with dynamic model switching)
• Response post-processing
• Logging
"""

import re
from config import AppConfig
from src.api.groq_client import GroqClient
from src.prompts.ecommerce_prompts import (
    EcommercePromptEngine,
    PromptConfig,
    PERSONAS,
)
from src.utils.logger import get_logger
from src.utils.security import SecurityUtils

logger = get_logger(__name__)


class ChatService:
    """
    High-level service consumed by app.py.

    Usage
    ─────
    svc = ChatService(cfg)
    reply = svc.get_response(user_message, history, settings)
    """

    OFF_TOPIC_REPLY = (
        "I specialise in shopping and e-commerce assistance.\n\n"
        "I can help you with **product discovery**, **order tracking**, "
        "**returns & refunds**, **comparisons**, and **store policies**.\n\n"
        "What can I help you shop for today?"
    )

    def __init__(self, cfg: AppConfig):
        self.cfg     = cfg
        self.engine  = EcommercePromptEngine()
        self.security = SecurityUtils(cfg)
        self._clients: dict[str, GroqClient] = {}
        self._default_client = self._get_client(cfg.GROQ_MODEL)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_response(
        self,
        user_message: str,
        history: list[dict],
        settings: dict,
    ) -> str:
        """
        Full pipeline from raw user input to final response string.
        """
        # 1. Input sanitisation
        clean_input = self.security.sanitise(user_message)
        if not clean_input:
            return "Please enter a valid message."

        # 2. Length guard
        if len(clean_input) > self.cfg.MAX_INPUT_LENGTH:
            return (
                f"Your message is too long (max {self.cfg.MAX_INPUT_LENGTH} chars). "
                "Please shorten it and try again."
            )

        # 3. Domain relevance check (fast keyword heuristic)
        if self.cfg.ENABLE_CONTENT_FILTER and not self._is_relevant(clean_input):
            logger.info("Off-topic query intercepted")
            return self.OFF_TOPIC_REPLY

        # 4. Build prompt config from UI settings
        prompt_cfg = PromptConfig(
            persona          = settings.get("persona", "friendly"),
            language         = settings.get("language", "English"),
            response_style   = settings.get("response_style", "detailed"),
            include_few_shot = settings.get("few_shot", True),
            store_name       = settings.get("store_name", "ShopMind Store"),
            extra_context    = settings.get("extra_context"),
        )

        # 5. Build system prompt
        system_prompt = self.engine.build_system_prompt(prompt_cfg)

        # 6. Format history + append current turn
        messages = self.engine.format_history(
            history, max_turns=self.cfg.MAX_HISTORY_TURNS
        )
        messages.append(self.engine.build_current_turn(clean_input))

        # 7. Get the right client for the selected model
        selected_model = settings.get("model", self.cfg.GROQ_MODEL)
        client = self._get_client(selected_model)

        # 8. Call Groq
        response = client.generate(
            messages       = messages,
            system_prompt  = system_prompt,
            temperature    = settings.get("temperature", self.cfg.DEFAULT_TEMPERATURE),
            max_tokens     = settings.get("max_tokens",  self.cfg.DEFAULT_MAX_TOKENS),
            top_p          = settings.get("top_p",       self.cfg.DEFAULT_TOP_P),
        )

        # 9. Post-process
        reply = self._post_process(response.text)
        logger.info(f"Response ready — {len(reply)} chars")
        return reply

    # ── Private ───────────────────────────────────────────────────────────────

    def _get_client(self, model: str) -> GroqClient:
        """Return a cached GroqClient for the given model."""
        if model not in self._clients:
            try:
                self.cfg.validate()
            except EnvironmentError as exc:
                logger.warning(str(exc))
            self._clients[model] = GroqClient(
                api_key     = self.cfg.GROQ_API_KEY,
                model       = model,
                base_url    = self.cfg.GROQ_BASE_URL,
                timeout     = self.cfg.REQUEST_TIMEOUT,
                max_retries = self.cfg.MAX_RETRIES,
                retry_delay = self.cfg.RETRY_DELAY_SEC,
            )
        return self._clients[model]

    def _is_relevant(self, text: str) -> bool:
        """
        Lightweight keyword-based topic guard.
        Returns True if the message looks e-commerce related.
        Passes greetings and short openers through automatically.
        """
        normalised = text.lower()
        # Always pass through short messages (greetings, simple queries)
        if len(normalised.split()) <= 6:
            return True
        return any(kw in normalised for kw in self.cfg.ALLOWED_TOPICS)

    @staticmethod
    def _post_process(text: str) -> str:
        """Trim whitespace, normalise line breaks, strip reasoning tags."""
        if not text:
            return "I'm sorry, I couldn't generate a response. Please try again."
        # Strip Qwen-style <think>...</think> reasoning blocks (complete or truncated)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Handle truncated think blocks (no closing tag due to max_tokens)
        text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
        return re.sub(r'\n{3,}', '\n\n', text).strip()

