from pathlib import Path

from utilitycode.logger import get_logger


logger = get_logger(__name__)


class FileValidator:

    @staticmethod
    def validate_archive(validation_input):

        logger.info("Starting file archive validation")

        try:
            source_path = Path(validation_input["SourcePath"])
            archive_path = Path(validation_input["ArchivePath"])

            logger.info(
                "Archive validation input | source=%s | archive=%s",
                source_path,
                archive_path
            )

            # The archived file is expected to retain the original filename
            archived_file = archive_path / source_path.name

            logger.info(
                "Expected archived file | path=%s",
                archived_file
            )

            source_result = FileValidator.validate_exists({
            "FilePath": str(source_path)
        })

            archive_result = FileValidator.validate_exists({
            "FilePath": str(archived_file)
        })

            source_exists = source_result["Evidence"]["FileExists"]
            archive_exists = archive_result["Evidence"]["FileExists"]

            logger.info(
                "Archive validation state | source_exists=%s | archive_exists=%s",
                source_exists,
                archive_exists
            )

            # A successful move means:
            # 1. Source file no longer exists
            # 2. Archived file exists
            if not source_exists and archive_exists:

                logger.info(
                    "Archive validation PASSED | file=%s",
                    source_path.name
                )

                return {
                    "Status": "PASS",
                    "Message": "File successfully archived",
                    "Evidence": {
                        "SourcePath": str(source_path),
                        "SourceExists": source_exists,
                        "ArchivePath": str(archive_path),
                        "ArchivedFile": str(archived_file),
                        "ArchiveExists": archive_exists
                    }
                }

            logger.warning(
                "Archive validation FAILED | file=%s | "
                "source_exists=%s | archive_exists=%s",
                source_path.name,
                source_exists,
                archive_exists
            )

            return {
                "Status": "FAIL",
                "Message": "File was not successfully archived",
                "Evidence": {
                    "SourcePath": str(source_path),
                    "SourceExists": source_exists,
                    "ArchivePath": str(archive_path),
                    "ArchivedFile": str(archived_file),
                    "ArchiveExists": archive_exists
                }
            }

        except KeyError as e:

            logger.error(
                "Archive validation failed | missing input field=%s",
                e
            )

            return {
                "Status": "FAIL",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during archive validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during archive validation: {e}",
                "Evidence": {}
            }

    @staticmethod
    def validate_exists(validation_input):

        logger.info("Starting file existence validation")

        try:
            file_path = Path(validation_input["FilePath"])

            logger.info(
                "Checking file existence | path=%s",
                file_path
            )

            file_exists = file_path.exists()

            if file_exists:
                logger.info(
                    "File existence validation PASSED | path=%s",
                    file_path
                )

                return {
                    "Status": "PASS",
                    "Message": "File exists",
                    "Evidence": {
                        "FilePath": str(file_path),
                        "FileExists": True
                    }
                }

            logger.warning(
                "File existence validation FAILED | path=%s",
                file_path
            )

            return {
                "Status": "FAIL",
                "Message": "File does not exist",
                "Evidence": {
                    "FilePath": str(file_path),
                    "FileExists": False
                }
            }

        except KeyError as e:

            logger.error(
                "File existence validation failed | missing input field=%s",
                e
            )

            return {
                "Status": "ERROR",
                "Message": f"Missing required validation input: {e}",
                "Evidence": {}
            }

        except Exception as e:

            logger.exception(
                "Unexpected error during file existence validation"
            )

            return {
                "Status": "ERROR",
                "Message": f"Unexpected error during file existence validation: {e}",
                "Evidence": {}
            }
