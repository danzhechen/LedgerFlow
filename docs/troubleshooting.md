# Troubleshooting Guide

Common issues and solutions for veritas-accounting.

## Table of Contents

- [Installation Issues](#installation-issues)
- [File Reading Issues](#file-reading-issues)
- [Processing Issues](#processing-issues)
- [Output Issues](#output-issues)
- [Performance Issues](#performance-issues)
- [Configuration Issues](#configuration-issues)

## Installation Issues

### Issue: "Command not found: veritas-accounting"

**Problem:** CLI command is not available after installation.

**Solutions:**
1. **Check Installation:**
   ```bash
   pip list | grep veritas-accounting
   ```

2. **Reinstall:**
   ```bash
   pip install -e .
   ```

3. **Use Python Module:**
   ```bash
   python -m veritas_accounting --help
   ```

4. **Check Virtual Environment:**
   - Ensure virtual environment is activated
   - Verify package is installed in correct environment

### Issue: "ModuleNotFoundError: No module named 'veritas_accounting'"

**Problem:** Python can't find the package.

**Solutions:**
1. **Check Installation:**
   ```bash
   pip show veritas-accounting
   ```

2. **Install in Development Mode:**
   ```bash
   pip install -e .
   ```

3. **Check Python Path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

4. **Verify Virtual Environment:**
   - Activate virtual environment
   - Check Python interpreter: `which python`

## File Reading Issues

### Issue: "File does not exist"

**Problem:** System can't find the specified file.

**Solutions:**
1. **Use Absolute Paths:**
   ```bash
   veritas-accounting process --input /full/path/to/journal.xlsx
   ```

2. **Check Current Directory:**
   ```bash
   pwd  # See current directory
   ls   # List files
   ```

3. **Verify File Permissions:**
   ```bash
   ls -l journal.xlsx  # Check permissions
   chmod 644 journal.xlsx  # Make readable if needed
   ```

4. **Check File Extension:**
   - Must be `.xlsx` (Excel 2007+ format)
   - Not `.xls` (old Excel format)

### Issue: "Permission denied"

**Problem:** File exists but can't be read.

**Solutions:**
1. **Check File Permissions:**
   ```bash
   chmod 644 journal.xlsx  # Make readable
   ```

2. **Check File Ownership:**
   ```bash
   ls -l journal.xlsx
   # If owned by different user, change ownership or permissions
   ```

3. **Check if File is Open:**
   - Close Excel if file is open
   - Close other programs using the file

### Issue: "Invalid Excel format" or "File is corrupted"

**Problem:** Excel file can't be read.

**Solutions:**
1. **Open and Re-save in Excel:**
   - Open file in Excel
   - Save as `.xlsx` format
   - Close Excel before running

2. **Check File Format:**
   - Must be Excel 2007+ format (`.xlsx`)
   - Not CSV, not old Excel (`.xls`)

3. **Verify File Integrity:**
   - Try opening in Excel manually
   - Check for corruption
   - Re-download if from external source

## Processing Issues

### Issue: "No matching rules found" for all entries

**Problem:** None of your journal entries match any mapping rules.

**Solutions:**
1. **Check Rule Conditions:**
   - Verify rule conditions match your data
   - Check `old_type` values in entries vs rules
   - Review year ranges in conditions

2. **Review Entry Data:**
   - Check `old_type` values in journal entries
   - Verify data matches rule expectations
   - Look for typos or case mismatches

3. **Test Rules:**
   ```bash
   # Validate rules first
   veritas-accounting validate --input journal.xlsx --rules rules.xlsx
   ```

4. **Add Missing Rules:**
   - Identify unmatched entry types
   - Create rules for those types
   - See [Rule Management Guide](./rule-management.md)

### Issue: "Amount mismatch in transformation"

**Problem:** Sum of ledger entries doesn't match journal entry amount.

**Solutions:**
1. **Check One-to-Many Rules:**
   - Verify `generates_multiple` rules split amounts correctly
   - Review rule logic for amount distribution

2. **Review Transformation:**
   - Check audit trail for transformation details
   - Verify all rules are applied
   - Check for missing entries

3. **Validate Rules:**
   - Ensure rules handle amounts correctly
   - Check for rounding issues
   - Verify account code mappings

### Issue: Processing is very slow

**Problem:** Processing takes a long time.

**Solutions:**
1. **Check File Size:**
   - Large files (>10,000 entries) may be slow
   - Consider splitting into smaller batches

2. **Review Validation Level:**
   ```bash
   # Use lenient validation for faster processing
   veritas-accounting process --input journal.xlsx --validation-level lenient
   ```

3. **Check System Resources:**
   - Ensure sufficient memory
   - Close other applications
   - Check disk space

4. **Optimize Rules:**
   - Reduce number of rules if possible
   - Simplify rule conditions
   - Review rule priority order

## Output Issues

### Issue: "Output files are empty"

**Problem:** Generated Excel files have no data.

**Solutions:**
1. **Check Input Data:**
   - Verify journal entries were read correctly
   - Check validation errors
   - Review error report

2. **Check Rules:**
   - Ensure rules match entries
   - Verify rules generate ledger entries
   - Review transformation log

3. **Check Processing:**
   - Review processing output for errors
   - Check if processing completed successfully
   - Verify no critical errors occurred

### Issue: "Chinese text displays incorrectly"

**Problem:** Chinese characters appear as garbled text.

**Solutions:**
1. **Check File Encoding:**
   - Ensure Excel files use UTF-8 encoding
   - Save files with UTF-8 encoding in Excel

2. **Check Terminal Encoding:**
   ```bash
   # Set UTF-8 encoding
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

3. **Verify System Support:**
   - Ensure system fonts support Chinese
   - Check Excel display settings
   - Verify file wasn't corrupted

### Issue: "Output files can't be opened in Excel"

**Problem:** Generated Excel files have errors when opening.

**Solutions:**
1. **Check File Format:**
   - Verify files are valid `.xlsx` format
   - Try opening with different Excel version
   - Check for file corruption

2. **Review File Size:**
   - Very large files may have issues
   - Check available disk space
   - Verify file wasn't truncated

3. **Re-generate:**
   ```bash
   # Re-run processing
   veritas-accounting process --input journal.xlsx --rules rules.xlsx
   ```

## Performance Issues

### Issue: "Out of memory" error

**Problem:** System runs out of memory during processing.

**Solutions:**
1. **Reduce Data Size:**
   - Process in smaller batches
   - Split large files
   - Remove unnecessary columns

2. **Increase System Memory:**
   - Close other applications
   - Increase virtual memory
   - Use system with more RAM

3. **Optimize Processing:**
   - Use lenient validation
   - Disable verbose logging
   - Process during off-peak hours

### Issue: Processing hangs or freezes

**Problem:** Processing stops responding.

**Solutions:**
1. **Check for Large Files:**
   - Very large files may take time
   - Check system resources
   - Monitor processing progress

2. **Check for Errors:**
   - Review error logs
   - Check for infinite loops in rules
   - Verify data integrity

3. **Interrupt and Restart:**
   ```bash
   # Press Ctrl+C to interrupt
   # Fix any issues
   # Restart processing
   ```

## Configuration Issues

### Issue: "Configuration file not found"

**Problem:** System can't find configuration file.

**Solutions:**
1. **Use Absolute Path:**
   ```bash
   veritas-accounting process --config /full/path/to/config.yaml
   ```

2. **Check File Location:**
   ```bash
   ls -la config.yaml  # Verify file exists
   ```

3. **Verify File Format:**
   - Must be YAML format (`.yaml` or `.yml`)
   - Check YAML syntax
   - Verify file isn't corrupted

### Issue: "Invalid configuration" error

**Problem:** Configuration file has errors.

**Solutions:**
1. **Check YAML Syntax:**
   - Verify proper indentation
   - Check for missing colons
   - Validate YAML format

2. **Validate Values:**
   - Check value types (strings, integers, booleans)
   - Verify file paths exist
   - Check value ranges

3. **Use YAML Validator:**
   ```bash
   # Test YAML syntax
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

### Issue: Environment variables not working

**Problem:** Environment variables aren't being used.

**Solutions:**
1. **Check Variable Names:**
   - Must start with `VERITAS_`
   - Use uppercase with underscores
   - Example: `VERITAS_JOURNAL_FILE`

2. **Verify Export:**
   ```bash
   # Check if variable is set
   echo $VERITAS_JOURNAL_FILE
   ```

3. **Set in Same Session:**
   - Export variables before running command
   - Or use in same command:
   ```bash
   VERITAS_JOURNAL_FILE=journal.xlsx veritas-accounting process
   ```

## General Troubleshooting Steps

### Step 1: Validate Input

Always validate input files first:
```bash
veritas-accounting validate --input journal.xlsx --rules rules.xlsx
```

### Step 2: Check Error Report

Review error report for detailed information:
- Open `error_report.xlsx`
- Check "Summary" sheet
- Review "Errors" sheet

### Step 3: Enable Verbose Logging

Get more detailed information:
```bash
veritas-accounting process --input journal.xlsx --verbose
```

### Step 4: Review Documentation

- Check [User Manual](./user-manual.md)
- Review [Error Handling Guide](./error-handling.md)
- See [Example Files](../examples/)

### Step 5: Test with Small Dataset

Test with a small subset first:
- Create test file with 10-20 entries
- Verify processing works
- Scale up to full dataset

## Still Having Issues?

If you've tried the above solutions and still have problems:

1. **Check Error Report:** Detailed information in `error_report.xlsx`
2. **Review Audit Trail:** Check `audit_trail.xlsx` for transformation details
3. **Validate All Inputs:** Use `validate` command to check files
4. **Check System Logs:** Review any log files generated
5. **Test with Examples:** Use example files to verify system works

---

**Related Guides:**
- [Error Handling Guide](./error-handling.md) - Detailed error information
- [User Manual](./user-manual.md) - Complete feature reference
- [Configuration Guide](./configuration.md) - Configuration options








