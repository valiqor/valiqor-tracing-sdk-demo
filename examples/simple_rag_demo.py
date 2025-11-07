"""
Valiqor Trace SDK - Simple RAG Demo

Demonstrates tracing a retrieval-augmented generation workflow.
"""

from valiqor import Trace


def main():
    """Run a simple RAG demo with tracing"""
    
    # Initialize tracer
    trace = Trace(app="rag-demo", env="dev")
    
    # User query
    user_query = "What were the key financial highlights for Q3 2024?"
    
    print(f"User Query: {user_query}\n")
    
    # Start trace session
    with trace.session(metadata={"query": user_query, "user": "demo_user"}):
        
        # Step 1: Document retrieval
        print("📚 Retrieving relevant documents...")
        trace.add_span(
            name="rag.retrieval",
            query=user_query,
            retriever="vectordb",
            embedding_model="text-embedding-3-small",
            top_k=5,
            documents_retrieved=5,
            latency_ms=234,
            top_scores=[0.89, 0.85, 0.82, 0.79, 0.75]
        )
        
        # Step 2: LLM generation with context
        print("🤖 Generating response...")
        trace.add_span(
            name="llm.call",
            model="gpt-4",
            provider="openai",
            prompt_template="Answer based on: {context}\n\nQuestion: {query}",
            context_length=3500,
            input_tokens=850,
            output_tokens=320,
            latency_ms=2100,
            cost_usd=0.0087,
            response="Q3 2024 showed strong performance with 18% revenue growth..."
        )
        
        # Step 3: Citation extraction
        print("🔗 Extracting citations...")
        trace.add_span(
            name="tool.extract_citations",
            input_docs=5,
            citations_found=3,
            latency_ms=85
        )
        
        # Step 4: Judge evaluation (optional quality check)
        print("✅ Evaluating response quality...")
        trace.add_span(
            name="judge.evaluate",
            metric="relevance",
            score=0.92,
            reasoning="Response directly addresses query with specific data",
            latency_ms=420
        )
    
    print("\n✅ RAG workflow completed with full tracing!")


if __name__ == "__main__":
    main()
