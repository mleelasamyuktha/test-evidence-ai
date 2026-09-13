from utilitycode.azure_blob import AzureBlobClient
import csv
import io
from utilitycode.logger import get_logger


logger = get_logger(__name__)

class FileValidator:
    @staticmethod
    def validate_archive(validation_input):
        logger.info("Starting file archive validation")

        try:
            source_path = validation_input["SourcePath"]
            archive_path = validation_input["ArchivePath"]

            logger.info(
                "Archive validation input | source=%s | archive=%s",
                source_path,
                archive_path
            )

            # Get the original filename from the source blob path
            file_name = source_path.rsplit("/", 1)[-1]

            # Build the expected archived blob path
            archived_file = archive_path.rstrip("/") + "/" + file_name

            logger.info(
                "Expected archived blob | path=%s",
                archived_file
            )

            # Reuse Azure-based existence validation
            source_result = FileValidator.validate_exists({
                "FilePath": source_path
            })

            archive_result = FileValidator.validate_exists({
                "FilePath": archived_file
            })

            source_exists = source_result["Evidence"]["FileExists"]
            archive_exists = archive_result["Evidence"]["FileExists"]

            logger.info(
                "Archive validation state | source_exists=%s | archive_exists=%s",
                source_exists,
                archive_exists
            )

            # Successful archive:
            # 1. Source blob no longer exists
            # 2. Archived blob exists
            if not source_exists and archive_exists:
                logger.info(
                    "Archive validation PASSED | file=%s",
                    file_name
                )

                return {
                    "Status": "PASS",
                    "Message": "File successfully archived",
                    "Evidence": {
                        "SourcePath": source_path,
                        "SourceExists": source_exists,
                        "ArchivePath": archive_path,
                        "ArchivedFile": archived_file,
                        "ArchiveExists": archive_exists,
                        "StorageType": "AzureBlob",
                    },
                }

            logger.warning(
                "Archive validation FAILED | file=%s | source_exists=%s | archive_exists=%s",
                file_name,
                source_exists,
                archive_exists
            )

            return {
                "Status": "FAIL",
                "Message": "File was not successfully archived",
                "Evidence": {
                    "SourcePath": source_path,
                    "SourceExists": source_exists,
                    "ArchivePath": archive_path,
                    "ArchivedFile": archived_file,
                    "ArchiveExists": archive_exists,
                    "StorageType": "AzureBlob",
                },
            }

        except KeyError as e:
            logger.error(
                "Archive validation failed | missing input field=%s",
                e
            )

            return {
                "Status": "FAIL",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }

        except Exception as e:
            logger.exception(
                "Unexpected error during archive validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during archive validation: {e}",
                "Evidence": {},
            }
            
    @staticmethod
    def validate_exists(validation_input):
        logger.info("Starting file existence validation")

        try:
            blob_path = validation_input["FilePath"]
            logger.info("Checking Azure blob existence | path=%s", blob_path)

            blob_client = AzureBlobClient()
            file_exists = blob_client.blob_exists(blob_path)

            if file_exists:
                logger.info("File existence validation PASSED | path=%s", blob_path)
                return {
                    "Status": "PASS",
                    "Message": "File exists",
                    "Evidence": {
                        "FilePath": blob_path,
                        "FileExists": True,
                        "StorageType": "AzureBlob",
                    },
                }

            logger.warning("File existence validation FAILED | path=%s", blob_path)
            return {
                "Status": "FAIL",
                "Message": "File does not exist",
                "Evidence": {
                    "FilePath": blob_path,
                    "FileExists": False,
                    "StorageType": "AzureBlob",
                },
            }

        except KeyError as e:
            logger.error("File existence validation failed | missing input field=%s", e)
            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }

        except Exception as e:
            logger.exception("Unexpected error during file existence validation")
            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during file existence validation: {e}",
                "Evidence": {},
            }
        
    @staticmethod
    def validate_header(validation_input):
        logger.info("Starting file header validation")

        try:
            blob_path = validation_input["FilePath"]
            logger.info("File header validation input | path=%s", blob_path)

            blob_client = AzureBlobClient()

            if not blob_client.blob_exists(blob_path):
                logger.warning("File header validation FAILED | blob does not exist | path=%s", blob_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {
                        "FilePath": blob_path,
                        "FileExists": False,
                        "StorageType": "AzureBlob",
                    },
                }

            blob_data = blob_client.download_blob(blob_path)

            file_content = io.StringIO(
                blob_data.decode("utf-8-sig")
            )

            reader = csv.reader(file_content)
            actual_headers = next(reader, [])

            logger.info("Actual file headers | headers=%s", actual_headers)

            if "ExpectedHeaders" not in validation_input:
                logger.info("Expected headers not supplied | returning actual headers")
                return {
                    "Status": "PASS",
                    "Message": "File headers successfully retrieved",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ActualHeaders": actual_headers,
                        "StorageType": "AzureBlob",
                    },
                }

            expected_headers = validation_input["ExpectedHeaders"]

            logger.info(
                "Expected headers supplied | expected=%s",
                expected_headers
            )

            headers_match = actual_headers == expected_headers

            logger.info(
                "Header comparison | expected=%s | actual=%s | match=%s",
                expected_headers,
                actual_headers,
                headers_match,
            )

            if headers_match:
                logger.info("File header validation PASSED | path=%s", blob_path)
                return {
                    "Status": "PASS",
                    "Message": "File headers match expected headers",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ExpectedHeaders": expected_headers,
                        "ActualHeaders": actual_headers,
                        "HeadersMatch": True,
                        "StorageType": "AzureBlob",
                    },
                }

            logger.warning("File header validation FAILED | path=%s", blob_path)

            return {
                "Status": "FAIL",
                "Message": "File headers do not match expected headers",
                "Evidence": {
                    "FilePath": blob_path,
                    "ExpectedHeaders": expected_headers,
                    "ActualHeaders": actual_headers,
                    "HeadersMatch": False,
                    "StorageType": "AzureBlob",
                },
            }

        except KeyError as e:
            logger.error("File header validation failed | missing input=%s", e)
            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }

        except Exception as e:
            logger.exception("Unexpected error during file header validation")
            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during file header validation: {e}",
                "Evidence": {},
            }
        
    @staticmethod
    def validate_count(validation_input):
        logger.info("Starting file count validation")

        try:
            blob_path = validation_input["FilePath"]
            logger.info("File count validation input | path=%s", blob_path)

            blob_client = AzureBlobClient()

            if not blob_client.blob_exists(blob_path):
                logger.warning("File count validation FAILED | blob does not exist | path=%s", blob_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {
                        "FilePath": blob_path,
                        "FileExists": False,
                        "StorageType": "AzureBlob",
                    },
                }

            blob_data = blob_client.download_blob(blob_path)

            file_content = io.StringIO(
                blob_data.decode("utf-8-sig")
            )

            reader = csv.reader(file_content)

            # Skip header
            next(reader, None)

            # Count data records
            actual_count = sum(1 for _ in reader)

            logger.info("Actual file record count | count=%s", actual_count)

            # ExpectedCount was not supplied.
            # Return the actual count only.
            if "ExpectedCount" not in validation_input:
                logger.info("Expected count not supplied | returning actual count")
                return {
                    "Status": "PASS",
                    "Message": "File record count successfully calculated",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ActualCount": actual_count,
                        "StorageType": "AzureBlob",
                    },
                }

            expected_count = validation_input["ExpectedCount"]

            logger.info(
                "Expected count supplied | expected=%s",
                expected_count
            )

            count_match = actual_count == expected_count

            logger.info(
                "Count comparison | expected=%s | actual=%s | match=%s",
                expected_count,
                actual_count,
                count_match,
            )

            if count_match:
                logger.info(
                    "File count validation PASSED | actual=%s | expected=%s",
                    actual_count,
                    expected_count,
                )

                return {
                    "Status": "PASS",
                    "Message": "File record count matches expected count",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ExpectedCount": expected_count,
                        "ActualCount": actual_count,
                        "CountMatch": True,
                        "StorageType": "AzureBlob",
                    },
                }

            logger.warning(
                "File count validation FAILED | actual=%s | expected=%s",
                actual_count,
                expected_count,
            )

            return {
                "Status": "FAIL",
                "Message": "File record count does not match expected count",
                "Evidence": {
                    "FilePath": blob_path,
                    "ExpectedCount": expected_count,
                    "ActualCount": actual_count,
                    "CountMatch": False,
                    "StorageType": "AzureBlob",
                },
            }

        except KeyError as e:
            logger.error("File count validation failed | missing input=%s", e)
            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }

        except Exception as e:
            logger.exception("Unexpected error during file count validation")
            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during file count validation: {e}",
                "Evidence": {},
            }
        
    @staticmethod
    def validate_format(validation_input):
        logger.info("Starting file format validation")

        try:
            blob_path = validation_input["FilePath"]
            logger.info("File format validation input | path=%s", blob_path)

            blob_client = AzureBlobClient()

            if not blob_client.blob_exists(blob_path):
                logger.warning("File format validation FAILED | blob does not exist | path=%s", blob_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {
                        "FilePath": blob_path,
                        "FileExists": False,
                        "StorageType": "AzureBlob",
                    },
                }

            # Get actual extension from Azure blob name
            file_name = blob_path.rsplit("/", 1)[-1]
            actual_format = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

            logger.info("Actual file format | format=%s", actual_format)

            # ExpectedFormat was not supplied.
            # Return the actual format only.
            if "ExpectedFormat" not in validation_input:
                logger.info("Expected format not supplied | returning actual format")
                return {
                    "Status": "PASS",
                    "Message": "File format successfully retrieved",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ActualFormat": actual_format,
                        "StorageType": "AzureBlob",
                    },
                }

            expected_format = validation_input["ExpectedFormat"]
            expected_format = str(expected_format).lstrip(".").lower()

            logger.info(
                "Expected format supplied | expected=%s",
                expected_format
            )

            format_match = actual_format == expected_format

            logger.info(
                "Format comparison | expected=%s | actual=%s | match=%s",
                expected_format,
                actual_format,
                format_match,
            )

            if format_match:
                logger.info("File format validation PASSED | path=%s", blob_path)

                return {
                    "Status": "PASS",
                    "Message": "File format matches expected format",
                    "Evidence": {
                        "FilePath": blob_path,
                        "ExpectedFormat": expected_format,
                        "ActualFormat": actual_format,
                        "FormatMatch": True,
                        "StorageType": "AzureBlob",
                    },
                }

            logger.warning("File format validation FAILED | path=%s", blob_path)

            return {
                "Status": "FAIL",
                "Message": "File format does not match expected format",
                "Evidence": {
                    "FilePath": blob_path,
                    "ExpectedFormat": expected_format,
                    "ActualFormat": actual_format,
                    "FormatMatch": False,
                    "StorageType": "AzureBlob",
                },
            }

        except KeyError as e:
            logger.error("File format validation failed | missing input=%s", e)
            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }

        except Exception as e:
            logger.exception("Unexpected error during file format validation")
            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during file format validation: {e}",
                "Evidence": {},
            }
