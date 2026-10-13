"""Gemini AI Vision Reasoning Service for PeekAI."""
from typing import Generator, Optional, Union, List
from google import genai
from google.genai import types
from src.config import Config


SYSTEM_PROMPT = """You are PeekAI, an elite, competition-grade technical AI copilot designed for campus placement tests, coding assessments (NeoPAT, LeetCode, HackerRank, Amcat, Mettl, TCS NQT), and technical interviews.

Your absolute highest priority is 100% FACTUAL, MATHEMATICAL, AND LOGICAL ACCURACY. Zero mistakes. Zero hallucinations.

═══════════════════════════════════════════════════════════════════════
🎯 PROTOCOL 1: MULTIPLE CHOICE QUESTIONS (MCQ) & ASSESSMENT TESTS
═══════════════════════════════════════════════════════════════════════
When the screen displays an exam or quiz question:

1. ⚠️ INVERSION & TRAP WORD DETECTION (MANDATORY):
   - Immediately check for negative/exclusionary keywords: "NOT", "EXCEPT", "INCORRECT", "FALSE", "LEAST", "INVALID", "NEVER", "CANNOT".
   - If present, NEVER select the true/valid statement. Select the ONE that is FALSE/INVALID.

2. 💻 CODE SNIPPET / OUTPUT PREDICTION MCQs:
   - Perform a line-by-line DRY-RUN EXECUTION.
   - Trace variable values across each iteration in an internal state table.
   - Enforce exact language rules:
     * Operator Precedence & Associativity (e.g., * / % over + -, bitwise precedence, short-circuit && and ||).
     * Pre-increment (++i) vs Post-increment (i++).
     * Integer division vs Floating-point division (e.g. 5 / 2 = 2 in C/C++/Java).
     * 0-based vs 1-based indexing, string 0-termination in C.
     * Pass-by-value vs Reference vs Pointer arithmetic.
     * Scope of static variables, global variables, and shadowing.
     * Type casting and overflow (e.g. byte/char bounds, Java Integer cache [-128, 127]).

3. 🌳 DATA STRUCTURES & ALGORITHM (DSA) MCQs:
   - Distinguish Best Case vs Average Case vs Worst Case (e.g., Quick Sort worst-case is O(n²), Hash Table search worst-case is O(n)).
   - Space Complexity: Distinguish Auxiliary Space from Total Space (e.g., Merge Sort requires O(n) auxiliary space and is NOT in-place).
   - Stable vs Unstable sorting algorithms.
   - Graph/Tree traversals: verify exact visit order (Inorder, Preorder, Postorder, Level order, BFS, DFS).

4. 🔬 OPTION ELIMINATION:
   - Systematically inspect ALL options (A, B, C, D).
   - Cross-check the derived answer against every choice to ensure no deceptive trap is selected.

5. 📋 OUTPUT FORMAT (Clear, instant, definitive):
   🎯 **Correct Option: [Letter] — [Exact Option Text]**

   **💡 Decisive Proof:**
   • [1-2 crisp bullet points with the exact derivation, variable output, or mathematical formula]
   • [Why the nearest trap/distractor option is wrong]

═══════════════════════════════════════════════════════════════════════
💻 PROTOCOL 2: CODING PROBLEMS (NeoPAT / LeetCode / Assessments)
═══════════════════════════════════════════════════════════════════════
If multiple screenshots are provided, they are consecutive scrolled slices (e.g., Problem Statement + Scrolled Constraints/Examples):
1. Synthesize all screenshots into a single complete problem context.
2. Detect the target programming language shown in the editor (Java, Python, C++, etc.). Default to Java/Python if unspecified.
3. Adhere strictly to ALL system constraints:
   - In-place modifications vs extra memory allowed (O(1) auxiliary space).
   - Time complexity limits (e.g., N <= 10^5 requires O(N) or O(N log N); O(N²) will TLE).
   - Corner cases: Empty array/string, single element, negative numbers, extreme values, duplicates.
4. Output format:
   Provide the COMPLETE, compilation-ready code block with standard I/O (Scanner/BufferedReader for Java, cin/cout for C++, sys.stdin for Python) matching the portal's test harness.
   Include a brief 2-line Time & Space Complexity analysis at the bottom.

═══════════════════════════════════════════════════════════════════════
🛠️ PROTOCOL 3: CODE ERRORS & TERMINAL DEBUGGING
═══════════════════════════════════════════════════════════════════════
1. State the exact root cause in 1 sentence.
2. Provide the exact drop-in code fix or command ready to execute.

═══════════════════════════════════════════════════════════════════════
General Rules:
- Direct, razor-sharp output. Zero conversational filler ("Sure!", "I can help with that", "Based on the image").
- Jump straight to the solution. 100% precision.
"""


class AIService:
    """Manages Gemini multimodal interactions and active chat sessions."""

    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._cached_api_key: Optional[str] = None
        self._active_chat = None
        self._active_model: Optional[str] = None
        self._last_image_bytes: Optional[bytes] = None

    def _get_client(self) -> genai.Client:
        """Initializes or returns a persistent Gemini client instance."""
        api_key = Config.get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Please add your API key in Settings.")

        need_new = False
        if self._client is None or self._cached_api_key != api_key:
            need_new = True
        else:
            try:
                # Check if underlying HTTP client was closed
                httpx_client = getattr(self._client._api_client, "_httpx_client", None)
                if httpx_client and httpx_client.is_closed:
                    need_new = True
            except Exception:
                need_new = True

        if need_new:
            self._client = genai.Client(api_key=api_key)
            self._cached_api_key = api_key

        return self._client

    def _create_generation_config(self, enable_thinking: bool = True) -> types.GenerateContentConfig:
        """Builds generation config with temperature 0.0 and deep reasoning thinking budget."""
        thinking = types.ThinkingConfig(thinking_budget=1024) if enable_thinking else None
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0,
            thinking_config=thinking,
        )

    def analyze_screen_stream(
        self,
        image_bytes: Union[bytes, List[bytes]],
        custom_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Starts a new screen analysis chat session with one or multiple sequential screenshots.
        Employs thinking budget for maximum assessment and coding accuracy.
        """
        client = self._get_client()
        model_name = Config.get_model()

        images_list = image_bytes if isinstance(image_bytes, list) else [image_bytes]
        self._last_image_bytes = images_list[0] if images_list else None

        # Multimodal PNG parts for 100% lossless OCR precision
        image_parts = [
            types.Part.from_bytes(data=img, mime_type="image/png")
            for img in images_list
        ]

        if len(images_list) > 1:
            prompt_text = (
                custom_prompt
                if custom_prompt
                else (
                    "CRITICAL ASSESSMENT MODE: These screenshots are sequential scrolled slices of the same assessment question.\n"
                    "1. Synthesize all sections together.\n"
                    "2. If MCQ: Carefully evaluate, check for NOT/EXCEPT trap words, trace any code line-by-line, eliminate all distractors, and output: "
                    "🎯 **Correct Option: [Letter] — [Option Text]** followed by the 2-line decisive proof.\n"
                    "3. If Coding problem: Provide the COMPLETE optimal compilable code fulfilling all time/space constraints."
                )
            )
        else:
            prompt_text = (
                custom_prompt
                if custom_prompt
                else (
                    "CRITICAL ASSESSMENT MODE: Analyze this screen with maximum precision.\n"
                    "• If MCQ / Quiz: Perform strict verification. Watch for trap words ('NOT', 'EXCEPT', 'FALSE'). Trace code line-by-line with exact operator precedence & variable states. Eliminate distractors. Output: 🎯 **Correct Option: [Letter] — [Option Text]** followed by the 2-line decisive proof.\n"
                    "• If Coding Problem: Detect the programming language and provide the complete, optimal, runnable solution adhering to all constraints.\n"
                    "• If Code Error / Bug: State root cause and provide the exact fix."
                )
            )

        contents = [prompt_text] + image_parts

        # Active, reliable Gemini models in prioritized order
        models_to_try = [model_name] + [
            m for m in ["gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-flash-latest"]
            if m != model_name
        ]

        last_err = None
        succeeded = False
        for current_model in models_to_try:
            # Try with thinking budget first; if model does not support it, fall back to standard config
            for use_thinking in [True, False]:
                try:
                    config = self._create_generation_config(enable_thinking=use_thinking)
                    self._active_chat = client.chats.create(model=current_model, config=config)
                    self._active_model = current_model
                    for chunk in self._active_chat.send_message_stream(contents):
                        if chunk.text:
                            yield chunk.text
                    succeeded = True
                    break
                except Exception as e:
                    last_err = e
                    err_str = str(e).lower()
                    if "thinking" in err_str:
                        # Retry without thinking config on the same model
                        continue
                    if "503" in str(e) or "unavailable" in err_str or "not_found" in err_str or "404" in str(e):
                        break  # Try next model
                    break  # Break inner loop to try next model

            if succeeded:
                break

        if not succeeded:
            yield f"\n\n**Error during analysis:** {str(last_err)}"

    def send_followup_stream(self, followup_text: str) -> Generator[str, None, None]:
        """
        Sends a follow-up query in the existing screen context and yields chunks.
        """
        if not self._active_chat:
            raise RuntimeError("No active screen analysis session. Please trigger a Peek first.")

        client = self._get_client()

        # Check if chat's client was closed and recover session with existing history
        try:
            if hasattr(self._active_chat, "_api_client"):
                httpx_client = getattr(self._active_chat._api_client, "_httpx_client", None)
                if httpx_client and httpx_client.is_closed:
                    history = self._active_chat.get_history()
                    config = self._create_generation_config()
                    self._active_chat = client.chats.create(
                        model=self._active_model or Config.get_model(),
                        config=config,
                        history=history
                    )
        except Exception:
            pass

        try:
            for chunk in self._active_chat.send_message_stream(followup_text):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # Automatic recovery fallback if connection was severed
            if "client has been closed" in str(e).lower():
                try:
                    history = self._active_chat.get_history()
                    self._client = genai.Client(api_key=Config.get_api_key())
                    config = self._create_generation_config()
                    self._active_chat = self._client.chats.create(
                        model=self._active_model or Config.get_model(),
                        config=config,
                        history=history
                    )
                    for chunk in self._active_chat.send_message_stream(followup_text):
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as rec_err:
                    yield f"\n\n**Error during follow-up:** {str(rec_err)}"
                    return
            yield f"\n\n**Error during follow-up:** {str(e)}"
