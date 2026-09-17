from app.ingestion_pipeline import IngestionPipeline


pipeline = IngestionPipeline()

result = pipeline.ingest_csv_to_table(
    source_file="SourceFolder/customer_data.csv",
    target_table="dbo.customer_data"
)

print(result)