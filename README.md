# TestEvidence AI

AI-powered automated data testing framework.

## Overview

TestEvidence AI converts developer stories into structured test cases using an LLM and executes those tests using deterministic Python validators.

### Core Principle

> LLM decides WHAT should be tested.
> Python decides HOW to test it.

## Architecture

Developer Story
      ↓
     LLM
      ↓
Structured Test Cases
      ↓
Test Executor
      ↓
Validation Catalog
      ↓
Deterministic Validators
      ↓
Evidence
      ↓
Test Report

## Project Structure

test-evidence-ai/
├── app/
├── validation/
├── config/
├── FolderStructure/
├── models/
├── utilitycode/
├── .gitignore
├── README.md
└── requirements.txt

## Blob Structure
TestEvidenceAI/
├── Logs/              # For Storing the Logs
├── Data/              # Data storage
├── SourceFolder/      # Input/source files
├── OutputFolder/      # Processed files
├── ArchiveFolder/     # Archived files
├── ReportingFolder/   # Generated reports
└── LLMOutput/         # LLM-generated test scenarios
