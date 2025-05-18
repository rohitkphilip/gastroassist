from typing import Dict, List, Any, Optional
import os
import json
import logging
from dotenv import load_dotenv


class LLMSummarizer:
    """
    Summarizes medical content using LLM with custom prompting for concise, factual output
    """

    def __init__(self):
        """Initialize the LLM summarizer"""
        # Load environment variables
        load_dotenv()

        # Determine which LLM service to use
        self.llm_service = os.getenv("LLM_SERVICE", "openai").lower()
        self.logger = logging.getLogger(__name__)

        if self.llm_service == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OPENAI_API_KEY environment variable is not set")
                self.client = OpenAI(api_key=api_key)
                self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            except ImportError:
                self.logger.error(
                    "OpenAI package not found. Install with: pip install openai")
                raise
        elif self.llm_service == "groq":
            try:
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError(
                        "GROQ_API_KEY environment variable is not set")
                self.client = Groq(api_key=api_key)
                self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
            except ImportError:
                self.logger.error(
                    "Groq package not found. Install with: pip install groq")
                raise
        else:
            raise ValueError(
                f"Unsupported LLM_SERVICE: {self.llm_service}. Use 'openai' or 'groq'")

    def summarize(self,
                  query: str,
                  extracted_contents: List[Dict[str, Any]],
                  max_tokens: int = 500) -> Dict[str, Any]:
        """
        Generate a concise, medically accurate summary from extracted contents

        Args:
            query: Original user query
            extracted_contents: List of extracted content dictionaries
            max_tokens: Maximum tokens for the summary response

        Returns:
            Dictionary with the summary and metadata
        """
        try:
            # Check if we have any valid extracted contents
            valid_contents = [content for content in extracted_contents
                              if content.get("extraction_success", False) and content.get("content")]

            if not valid_contents:
                return {
                    "summary": "No valid content could be extracted to answer your query. Please try with a different search term or consult direct medical sources.",
                    "sources": [],
                    "query": query,
                    "model_used": self.model,
                    "token_count": 0
                }

            # Prepare the context from extracted contents
            context = self._prepare_context(valid_contents)

            # Create the prompt with medical-specific instructions
            prompt = self._create_medical_prompt(query, context)

            # Log the model being used
            self.logger.info(f"Using {self.llm_service} model: {self.model}")

            # Generate the summary using the LLM
            if self.llm_service == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a gastroenterology expert assistant providing concise, accurate medical information with proper citations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,  # Slightly higher temperature for GPT-3.5 Turbo to maintain coherence
                    n=1
                )
            elif self.llm_service == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a gastroenterology expert assistant providing concise, accurate medical information with proper citations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,
                    n=1
                )

            # Extract the generated summary
            summary_text = response.choices[0].message.content.strip()

            # Check for empty summary
            if not summary_text:
                summary_text = "Unable to generate a summary from the available content. The extracted information may not be relevant to your query."

            # Create metadata for the summary
            sources = []
            for i, content in enumerate(valid_contents):
                sources.append({
                    "id": f"source-{i+1}",
                    "title": content.get("title", "Unknown title"),
                    "url": content.get("source_url", ""),
                    "author": content.get("author", "Unknown"),
                    "published_date": content.get("published_date", "")
                })

            # Calculate token count safely
            token_count = len(summary_text.split()) if summary_text else 0

            # Return the summary and metadata
            return {
                "summary": summary_text,
                "sources": sources,
                "query": query,
                "model_used": self.model,
                "token_count": token_count
            }

        except Exception as e:
            self.logger.error(f"Error in LLM summarization: {str(e)}")
            # Return an error response with basic information
            return {
                "summary": f"Unable to generate summary due to an error: {str(e)}",
                "sources": [],
                "query": query,
                "model_used": self.model,
                "token_count": 0,
                "error": str(e)
            }

    def _prepare_context(self, extracted_contents: List[Dict[str, Any]]) -> str:
        """
        Prepare the context from the extracted contents

        Args:
            extracted_contents: List of extracted content dictionaries

        Returns:
            String containing formatted context
        """
        context_parts = []

        for i, content in enumerate(extracted_contents):
            # Format the content with metadata
            context_part = f"### SOURCE {i+1}: {content.get('title', 'Unknown title')}\n"
            context_part += f"URL: {content.get('source_url', 'No URL')}\n"
            if content.get("author"):
                context_part += f"Author: {content.get('author')}\n"
            if content.get("published_date"):
                context_part += f"Date: {content.get('published_date')}\n"

            # For GPT-3.5 Turbo, we need to be careful about context length
            # Extract and truncate the content to a reasonable length
            content_text = content.get('content', '')

            # Handle None values
            if content_text is None:
                content_text = "No content available"

            # If content is very long, truncate it to ~4000 chars to fit in context window
            if len(content_text) > 4000:
                content_text = content_text[:4000] + \
                    "... [content truncated due to length]"

            # Add the main content
            context_part += f"\nCONTENT:\n{content_text}\n\n"

            context_parts.append(context_part)

        # Join all context parts
        return "\n".join(context_parts)

    def _create_medical_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt specifically designed for medical summarization

        Args:
            query: Original user query
            context: Formatted context from extracted contents

        Returns:
            Prompt string
        """
        # Modified prompt optimized for GPT-3.5 Turbo's capabilities
        prompt = f"""
As a gastroenterology expert, provide a concise, accurate response to this query:

QUERY: {query}

Below are sources from medical literature. Use these to formulate your response.

{context}

INSTRUCTIONS:
1. Only include medical facts directly supported by the sources
2. Be brief and crisp - focus on the most relevant information
3. Use clear medical terminology for healthcare professionals
4. Cite sources using [SOURCE X] notation after each fact
5. If sources conflict, present both perspectives
6. If information is limited, state this clearly
7. Avoid personal opinions or unsupported recommendations
8. Use bullet points for readability when appropriate
9. Keep your response to 3-7 sentences for straightforward queries
10. Focus on the direct answer to the query

YOUR RESPONSE:
"""
        return prompt

    def set_model(self, model_name: str) -> None:
        """
        Change the LLM model used for summarization

        Args:
            model_name: Name of the model to use
                (e.g., "gpt-3.5-turbo" for OpenAI, "llama3-70b-8192" for Groq)
        """
        self.logger.info(f"Changing model from {self.model} to {model_name}")
        self.model = model_name

    def set_service(self, service_name: str) -> None:
        """
        Change the LLM service used for summarization

        Args:
            service_name: Name of the service to use ("openai" or "groq")
        """
        if service_name.lower() not in ["openai", "groq"]:
            raise ValueError(
                f"Unsupported LLM service: {service_name}. Use 'openai' or 'groq'")

        if service_name.lower() != self.llm_service:
            self.logger.info(
                f"Changing LLM service from {self.llm_service} to {service_name}")
            # Reinitialize the client with the new service
            self.__init__()
