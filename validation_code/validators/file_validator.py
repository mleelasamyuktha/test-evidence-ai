from pathlib import Path
import csv
from utilitycode.logger import get_logger


logger = get_logger(__name__)

class FileValidator:
    @staticmethod
    def validate_archive(validation_input):
        logger.info("Starting file archive validation")
        try:
            source_path = Path(validation_input["SourcePath"])
            archive_path = Path(validation_input["ArchivePath"])
            logger.info("Archive validation input | source=%s | archive=%s", source_path,archive_path)

            # The archived file is expected to retain the original filename
            archived_file = archive_path / source_path.name
            logger.info("Expected archived file | path=%s", archived_file)

            source_result = FileValidator.validate_exists({"FilePath": str(source_path)})
            archive_result = FileValidator.validate_exists({"FilePath": str(archived_file)})

            source_exists = source_result["Evidence"]["FileExists"]
            archive_exists = archive_result["Evidence"]["FileExists"]
            logger.info("Archive validation state | source_exists=%s | archive_exists=%s", source_exists, archive_exists)

            # A successful move means:
            # 1. Source file no longer exists
            # 2. Archived file exists
            if not source_exists and archive_exists:
                logger.info("Archive validation PASSED | file=%s", source_path.name)
                return {
                    "Status": "PASS",
                    "Message": "File successfully archived",
                    "Evidence": {
                        "SourcePath": str(source_path),
                        "SourceExists": source_exists,
                        "ArchivePath": str(archive_path),
                        "ArchivedFile": str(archived_file),
                        "ArchiveExists": archive_exists,
                    },
                }
            logger.warning("Archive validation FAILED | file=%s | source_exists=%s | archive_exists=%s", source_path.name, source_exists, archive_exists)
            return {
                "Status": "FAIL",
                "Message": "File was not successfully archived",
                "Evidence": {
                    "SourcePath": str(source_path),
                    "SourceExists": source_exists,
                    "ArchivePath": str(archive_path),
                    "ArchivedFile": str(archived_file),
                    "ArchiveExists": archive_exists,
                },
            }
        except KeyError as e:
            logger.error("Archive validation failed | missing input field=%s", e)
            return {
                "Status": "FAIL",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {},
            }
        except Exception as e:
            logger.exception("Unexpected error during archive validation")
            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during archive validation: {e}",
                "Evidence": {},
            }
        
    @staticmethod
    def validate_exists(validation_input):
        logger.info("Starting file existence validation")

        try:
            file_path = Path(validation_input["FilePath"])
            logger.info("Checking file existence | path=%s", file_path)

            file_exists = file_path.exists()
            if file_exists:
                logger.info("File existence validation PASSED | path=%s", file_path)
                return {
                    "Status": "PASS",
                    "Message": "File exists",
                    "Evidence": {"FilePath": str(file_path), "FileExists": True},
                }
            logger.warning("File existence validation FAILED | path=%s", file_path)
            return {
                "Status": "FAIL",
                "Message": "File does not exist",
                "Evidence": {"FilePath": str(file_path), "FileExists": False},
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
            file_path = Path(validation_input["FilePath"])
            logger.info("File header validation input | path=%s", file_path)

            if not file_path.is_file():
                logger.warning("File header validation FAILED | file does not exist | path=%s", file_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {"FilePath": str(file_path), "FileExists": False},
                }
            
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file)
                actual_headers = next(reader, [])
            logger.info("Actual file headers | headers=%s", actual_headers)

            # ExpectedHeaders was not supplied.
            # Return the actual headers only.
            if "ExpectedHeaders" not in validation_input:
                logger.info("Expected headers not supplied | returning actual headers")
                return {
                    "Status": "PASS",
                    "Message": "File headers successfully retrieved",
                    "Evidence": {
                        "FilePath": str(file_path),
                        "ActualHeaders": actual_headers,
                    },
                }
            expected_headers = validation_input["ExpectedHeaders"]
            logger.info("Expected headers supplied | expected=%s", expected_headers)

            headers_match = actual_headers == expected_headers
            logger.info(
                "Header comparison | expected=%s | actual=%s | match=%s",
                expected_headers,
                actual_headers,
                headers_match,
            )

            if headers_match:
                logger.info("File header validation PASSED | path=%s", file_path)
                return {
                    "Status": "PASS",
                    "Message": "File headers match expected headers",
                    "Evidence": {
                        "FilePath": str(file_path),
                        "ExpectedHeaders": expected_headers,
                        "ActualHeaders": actual_headers,
                        "HeadersMatch": True,
                    },
                }
            logger.warning("File header validation FAILED | path=%s", file_path)

            return {
                "Status": "FAIL",
                "Message": "File headers do not match expected headers",
                "Evidence": {
                    "FilePath": str(file_path),
                    "ExpectedHeaders": expected_headers,
                    "ActualHeaders": actual_headers,
                    "HeadersMatch": False,
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
            file_path = Path(validation_input["FilePath"])
            logger.info("File count validation input | path=%s", file_path)

            if not file_path.is_file():
                logger.warning("File count validation FAILED | file does not exist | path=%s", file_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {"FilePath": str(file_path), "FileExists": False},
                }
            
            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file)
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
                        "FilePath": str(file_path),
                        "ActualCount": actual_count,
                    },
                }
            
            expected_count = validation_input["ExpectedCount"]
            logger.info("Expected count supplied | expected=%s", expected_count)
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
                        "FilePath": str(file_path),
                        "ExpectedCount": expected_count,
                        "ActualCount": actual_count,
                        "CountMatch": True,
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
                    "FilePath": str(file_path),
                    "ExpectedCount": expected_count,
                    "ActualCount": actual_count,
                    "CountMatch": False,
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
            file_path = Path(validation_input["FilePath"])
            logger.info("File format validation input | path=%s", file_path)

            if not file_path.is_file():
                logger.warning("File format validation FAILED | file does not exist | path=%s", file_path)
                return {
                    "Status": "FAIL",
                    "Message": "File does not exist",
                    "Evidence": {"FilePath": str(file_path), "FileExists": False},
                }
            
            # Get actual extension from filename
            actual_format = file_path.suffix.lstrip(".").lower()
            logger.info("Actual file format | format=%s", actual_format)

            # ExpectedFormat was not supplied.
            # Return the actual format only.
            if "ExpectedFormat" not in validation_input:
                logger.info("Expected format not supplied | returning actual format")
                return {
                    "Status": "PASS",
                    "Message": "File format successfully retrieved",
                    "Evidence": {
                        "FilePath": str(file_path),
                        "ActualFormat": actual_format,
                    },
                }
            
            expected_format = validation_input["ExpectedFormat"]
            # Normalize expected format
            expected_format = str(expected_format).lstrip(".").lower()
            logger.info("Expected format supplied | expected=%s", expected_format)
            format_match = actual_format == expected_format
            logger.info(
                "Format comparison | expected=%s | actual=%s | match=%s",
                expected_format,
                actual_format,
                format_match,
            )

            if format_match:
                logger.info("File format validation PASSED | path=%s", file_path)
                return {
                    "Status": "PASS",
                    "Message": "File format matches expected format",
                    "Evidence": {
                        "FilePath": str(file_path),
                        "ExpectedFormat": expected_format,
                        "ActualFormat": actual_format,
                        "FormatMatch": True,
                    },
                }
            logger.warning("File format validation FAILED | path=%s", file_path)

            return {
                "Status": "FAIL",
                "Message": "File format does not match expected format",
                "Evidence": {
                    "FilePath": str(file_path),
                    "ExpectedFormat": expected_format,
                    "ActualFormat": actual_format,
                    "FormatMatch": False,
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
