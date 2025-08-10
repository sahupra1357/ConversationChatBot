from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter,
)
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index import core as llama_core


import os
from dotenv import load_dotenv

def init_observability():
    # Load environment variables from .env file
    load_dotenv()

    # # Add Phoenix API Key for tracing
    # os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = os.environ["PHOENIX_API_KEY"]

    # # Add Phoenix
    # span_phoenix_processor = SimpleSpanProcessor(
    #     HTTPSpanExporter(endpoint="https://app.phoenix.arize.com/v1/traces")
    # )

    # # Add them to the tracer
    # tracer_provider = trace_sdk.TracerProvider()
    # tracer_provider.add_span_processor(span_processor=span_phoenix_processor)

    # # Instrument the application
    # LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

    PHOENIX_API_KEY = os.environ["PHOENIX_API_KEY"]
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
    llama_core.set_global_handler(
        "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
    )    


