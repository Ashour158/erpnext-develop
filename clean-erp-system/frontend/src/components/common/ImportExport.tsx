// Import/Export Component
// Universal import/export functionality for all modules

import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Alert,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  FileDownload,
  FileUpload,
  GetApp,
  Publish,
  CheckCircle,
  Error,
  Warning,
  Info,
  Close,
  Refresh,
  Settings,
  Description,
  TableChart,
  PictureAsPdf,
  CloudDownload,
  CloudUpload,
  Speed,
  Storage,
  Timeline
} from '@mui/icons-material';

interface ImportExportProps {
  module: string;
  entity: string;
  onImport?: (data: any[]) => void;
  onExport?: (format: string, filters?: any) => void;
  availableFields?: string[];
  sampleData?: any[];
  onClose?: () => void;
}

const ImportExport: React.FC<ImportExportProps> = ({
  module,
  entity,
  onImport,
  onExport,
  availableFields = [],
  sampleData = [],
  onClose
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [importStep, setImportStep] = useState(0);
  const [exportStep, setExportStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importFormat, setImportFormat] = useState<'csv' | 'excel' | 'json'>('csv');
  const [exportFormat, setExportFormat] = useState<'csv' | 'excel' | 'pdf' | 'json'>('csv');
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [importFilters, setImportFilters] = useState<any>({});
  const [exportFilters, setExportFilters] = useState<any>({});
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const [validationResults, setValidationResults] = useState<any>(null);
  const [importProgress, setImportProgress] = useState(0);
  const [exportProgress, setExportProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setImportStep(1);
    }
  };

  const handleFieldMapping = useCallback(() => {
    if (!selectedFile) return;
    
    setLoading(true);
    setError('');
    
    // Simulate field mapping analysis
    setTimeout(() => {
      const mockMapping = {
        'Name': 'name',
        'Email': 'email',
        'Phone': 'phone',
        'Company': 'company',
        'Status': 'status'
      };
      setMapping(mockMapping);
      setImportStep(2);
      setLoading(false);
    }, 2000);
  }, [selectedFile]);

  const handleValidation = useCallback(() => {
    setLoading(true);
    setError('');
    
    // Simulate validation
    setTimeout(() => {
      const mockValidation = {
        totalRows: 100,
        validRows: 95,
        invalidRows: 5,
        errors: [
          { row: 10, field: 'email', message: 'Invalid email format' },
          { row: 25, field: 'phone', message: 'Phone number required' }
        ],
        warnings: [
          { row: 5, field: 'company', message: 'Company name is very long' }
        ]
      };
      setValidationResults(mockValidation);
      setImportStep(3);
      setLoading(false);
    }, 3000);
  }, []);

  const handleImport = useCallback(() => {
    setLoading(true);
    setError('');
    setImportProgress(0);
    
    // Simulate import process
    const interval = setInterval(() => {
      setImportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setLoading(false);
          setSuccess('Import completed successfully');
          onImport?.(sampleData);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  }, [onImport, sampleData]);

  const handleExport = useCallback(() => {
    setLoading(true);
    setError('');
    setExportProgress(0);
    
    // Simulate export process
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setLoading(false);
          setSuccess('Export completed successfully');
          onExport?.(exportFormat, exportFilters);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  }, [onExport, exportFormat, exportFilters]);

  const renderImportDialog = () => (
    <Dialog open={activeStep === 0} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Import {entity}</DialogTitle>
      <DialogContent>
        <Stepper activeStep={importStep} orientation="vertical">
          <Step>
            <StepLabel>Select File</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls,.json"
                  onChange={handleFileSelect}
                  style={{ marginBottom: 16 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Supported formats: CSV, Excel (.xlsx, .xls), JSON
                </Typography>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Field Mapping</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Map the columns from your file to the system fields:
                </Typography>
                {Object.entries(mapping).map(([fileField, systemField]) => (
                  <Box key={fileField} display="flex" alignItems="center" gap={2} py={1}>
                    <Typography variant="body2" sx={{ minWidth: 120 }}>
                      {fileField}
                    </Typography>
                    <Typography variant="body2">→</Typography>
                    <FormControl size="small" sx={{ minWidth: 200 }}>
                      <Select
                        value={systemField}
                        onChange={(e) => setMapping(prev => ({ ...prev, [fileField]: e.target.value }))}
                      >
                        {availableFields.map(field => (
                          <MenuItem key={field} value={field}>
                            {field}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>
                ))}
                <Button
                  variant="contained"
                  onClick={handleFieldMapping}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Analyzing...' : 'Analyze File'}
                </Button>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Validation</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                {validationResults && (
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Validation Results
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2">
                            Total Rows: {validationResults.totalRows}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="success.main">
                            Valid Rows: {validationResults.validRows}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="error.main">
                            Invalid Rows: {validationResults.invalidRows}
                          </Typography>
                        </Grid>
                      </Grid>
                      
                      {validationResults.errors.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" color="error">
                            Errors:
                          </Typography>
                          {validationResults.errors.map((error: any, index: number) => (
                            <Typography key={index} variant="body2" color="error">
                              Row {error.row}: {error.message}
                            </Typography>
                          ))}
                        </Box>
                      )}
                      
                      {validationResults.warnings.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" color="warning.main">
                            Warnings:
                          </Typography>
                          {validationResults.warnings.map((warning: any, index: number) => (
                            <Typography key={index} variant="body2" color="warning.main">
                              Row {warning.row}: {warning.message}
                            </Typography>
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}
                <Button
                  variant="contained"
                  onClick={handleValidation}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Validating...' : 'Validate Data'}
                </Button>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Import</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                {loading && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Importing data... {importProgress}%
                    </Typography>
                    <LinearProgress variant="determinate" value={importProgress} />
                  </Box>
                )}
                <Button
                  variant="contained"
                  onClick={handleImport}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Importing...' : 'Start Import'}
                </Button>
              </Box>
            </StepContent>
          </Step>
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );

  const renderExportDialog = () => (
    <Dialog open={activeStep === 1} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Export {entity}</DialogTitle>
      <DialogContent>
        <Stepper activeStep={exportStep} orientation="vertical">
          <Step>
            <StepLabel>Select Format</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Export Format</InputLabel>
                  <Select
                    value={exportFormat}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                  >
                    <MenuItem value="csv">
                      <Box display="flex" alignItems="center" gap={1}>
                        <TableChart />
                        CSV
                      </Box>
                    </MenuItem>
                    <MenuItem value="excel">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Description />
                        Excel
                      </Box>
                    </MenuItem>
                    <MenuItem value="pdf">
                      <Box display="flex" alignItems="center" gap={1}>
                        <PictureAsPdf />
                        PDF
                      </Box>
                    </MenuItem>
                    <MenuItem value="json">
                      <Box display="flex" alignItems="center" gap={1}>
                        <Description />
                        JSON
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="contained"
                  onClick={() => setExportStep(1)}
                >
                  Next
                </Button>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Select Fields</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Select the fields to include in the export:
                </Typography>
                <FormGroup>
                  {availableFields.map(field => (
                    <FormControlLabel
                      key={field}
                      control={
                        <Checkbox
                          checked={selectedFields.includes(field)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedFields([...selectedFields, field]);
                            } else {
                              setSelectedFields(selectedFields.filter(f => f !== field));
                            }
                          }}
                        />
                      }
                      label={field}
                    />
                  ))}
                </FormGroup>
                <Button
                  variant="contained"
                  onClick={() => setExportStep(2)}
                  disabled={selectedFields.length === 0}
                  sx={{ mt: 2 }}
                >
                  Next
                </Button>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Apply Filters</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Apply filters to the export (optional):
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Date From"
                      type="date"
                      value={exportFilters.dateFrom || ''}
                      onChange={(e) => setExportFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Date To"
                      type="date"
                      value={exportFilters.dateTo || ''}
                      onChange={(e) => setExportFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Status</InputLabel>
                      <Select
                        value={exportFilters.status || ''}
                        onChange={(e) => setExportFilters(prev => ({ ...prev, status: e.target.value }))}
                      >
                        <MenuItem value="">All</MenuItem>
                        <MenuItem value="active">Active</MenuItem>
                        <MenuItem value="inactive">Inactive</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
                <Button
                  variant="contained"
                  onClick={() => setExportStep(3)}
                  sx={{ mt: 2 }}
                >
                  Next
                </Button>
              </Box>
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Export</StepLabel>
            <StepContent>
              <Box sx={{ mt: 2 }}>
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Export Summary
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Format: {exportFormat.toUpperCase()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          Fields: {selectedFields.length}
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="body2">
                          Selected Fields: {selectedFields.join(', ')}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
                
                {loading && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Exporting data... {exportProgress}%
                    </Typography>
                    <LinearProgress variant="determinate" value={exportProgress} />
                  </Box>
                )}
                
                <Button
                  variant="contained"
                  onClick={handleExport}
                  disabled={loading}
                  startIcon={<FileDownload />}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Exporting...' : 'Start Export'}
                </Button>
              </Box>
            </StepContent>
          </Step>
        </Stepper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box>
      {/* Import/Export Buttons */}
      <Box display="flex" gap={2} sx={{ mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<FileUpload />}
          onClick={() => setActiveStep(0)}
        >
          Import {entity}
        </Button>
        <Button
          variant="outlined"
          startIcon={<FileDownload />}
          onClick={() => setActiveStep(1)}
        >
          Export {entity}
        </Button>
      </Box>

      {/* Import Dialog */}
      {renderImportDialog()}

      {/* Export Dialog */}
      {renderExportDialog()}

      {/* Success/Error Messages */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ImportExport;
