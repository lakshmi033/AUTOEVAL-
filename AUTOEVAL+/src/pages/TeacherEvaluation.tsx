import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Upload, FileText, ScanText, X } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface LocationState {
  student?: {
    id: string;
    name: string;
    rollNumber: string;
  };
  reEvaluate?: boolean;
}

const TeacherEvaluation = () => {
  const { classId, studentId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { student, reEvaluate } = (location.state as LocationState) || {};
  const isReEvaluateMode = Boolean(reEvaluate);

  const [answerSheet, setAnswerSheet] = useState<File | null>(null);
  const [answerSheetPreview, setAnswerSheetPreview] = useState<string | null>(null);
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [answerKeyPreview, setAnswerKeyPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [answerSheetId, setAnswerSheetId] = useState<number | null>(null);
  const [storedAnswerKeyId, setStoredAnswerKeyId] = useState<number | null>(null);
  const [storedKeyFilename, setStoredKeyFilename] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [autoLoadDone, setAutoLoadDone] = useState(false);

  const handleAnswerSheetUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAnswerSheet(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setAnswerSheetPreview(reader.result as string);
      };
      reader.readAsDataURL(file);

      toast({
        title: "Answer Sheet Uploaded",
        description: `${file.name} has been uploaded successfully.`,
      });
    }
  };

  const handleAnswerKeyUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAnswerKey(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setAnswerKeyPreview(reader.result as string);
      };
      reader.readAsDataURL(file);

      toast({
        title: "Answer Key Uploaded",
        description: `${file.name} has been uploaded successfully.`,
      });
    }
  };

  const clearAnswerSheet = () => {
    setAnswerSheet(null);
    setAnswerSheetPreview(null);
    setExtractedText('');
    setAnswerSheetId(null);
  };

  const clearAnswerKey = () => {
    setAnswerKey(null);
    setAnswerKeyPreview(null);
    setStoredAnswerKeyId(null);
    setStoredKeyFilename(null);
  };

  const loadStoredOCR = async () => {
    if (!studentId) return;
    setIsProcessing(true);
    try {
      const response = await api.get(`/stored-sheet/${studentId}`);
      const data = response.data;
      setExtractedText(data.ocr_text);
      setAnswerSheetId(data.answer_sheet_id);
      toast({
        title: 'Stored OCR Loaded',
        description: `Loaded stored answer sheet "${data.filename}" successfully.`,
      });
    } catch (error: any) {
      toast({
        title: 'No Stored Sheet Found',
        description: error.response?.data?.detail || 'No previous OCR data found for this student.',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const loadStoredKey = async () => {
    setIsProcessing(true);
    try {
      const response = await api.get('/stored-key');
      const data = response.data;
      setStoredAnswerKeyId(data.answer_key_id);
      setStoredKeyFilename(data.filename);
      toast({
        title: 'Stored Answer Key Loaded',
        description: `Answer key "${data.filename}" loaded from database.`,
      });
    } catch (error: any) {
      toast({
        title: 'No Stored Key Found',
        description: error.response?.data?.detail || 'No stored answer key found. Please upload one.',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ── AUTO-LOAD on Re-Evaluate mode ──────────────────────────────
  // Triggered when navigated here with reEvaluate:true in router state.
  // Fetches stored OCR text + stored answer key from DB — zero new API calls.
  useEffect(() => {
    if (!isReEvaluateMode || autoLoadDone || !studentId) return;
    setAutoLoadDone(true); // prevent double-fire

    const autoLoad = async () => {
      setIsProcessing(true);
      let sheetOk = false;
      let keyOk = false;

      // Load stored OCR
      try {
        const sheetRes = await api.get(`/stored-sheet/${studentId}`);
        setExtractedText(sheetRes.data.ocr_text);
        setAnswerSheetId(sheetRes.data.answer_sheet_id);
        sheetOk = true;
      } catch {
        toast({ title: 'Stored Sheet Error', description: 'Could not load stored OCR text.', variant: 'destructive' });
      }

      // Load stored Answer Key
      try {
        const keyRes = await api.get('/stored-key');
        setStoredAnswerKeyId(keyRes.data.answer_key_id);
        setStoredKeyFilename(keyRes.data.filename);
        keyOk = true;
      } catch {
        toast({ title: 'Stored Key Error', description: 'Could not load stored answer key.', variant: 'destructive' });
      }

      setIsProcessing(false);

      if (sheetOk && keyOk) {
        toast({
          title: '✅ Re-Evaluation Ready',
          description: 'Stored OCR and answer key loaded. Click Evaluate Answers to proceed.',
        });
      }
    };

    autoLoad();
  }, [isReEvaluateMode, studentId, autoLoadDone]);
  // ───────────────────────────────────────────────────────────────

  const handleProcessOCR = async () => {
    if (!answerSheet) {
      toast({
        title: "No Answer Sheet",
        description: "Please upload an answer sheet first.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('student_id', studentId || '');
      formData.append('file', answerSheet);

      // Use the shared api instance which handles base URL and auth tokens
      // Note: We need to set 'Content-Type': 'multipart/form-data', 
      // but Axios often handles this automatically for FormData.
      // Explicitly setting it just in case.
      const response = await api.post('/upload-answer-sheet', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;

      if (data.error) {
        toast({
          title: "OCR Warning",
          description: data.error,
          variant: "destructive",
        });
        setExtractedText(""); // Clear extracted text if there's an error
        setAnswerSheetId(null);
      } else {
        setExtractedText(data.ocr_text);
        setAnswerSheetId(data.answer_sheet_id);
        if (data.source) {
          toast({
            title: "OCR Successful",
            description: `Extracted using: ${data.source}`,
            variant: data.source.includes("Cloud") ? "default" : "destructive", // Warn if local
          });
        } else {
          toast({
            title: "OCR Processing Complete",
            description: "Text has been extracted from the answer sheet.",
          });
        }
      }

    } catch (error: any) {
      console.error("OCR Error:", error);
      toast({
        title: "OCR Error",
        description: error.response?.data?.detail || "Failed to process answer sheet. Please try again.",
        variant: "destructive",
      });
      setExtractedText("");
      setAnswerSheetId(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEvaluate = async () => {
    if (!answerSheetId || (!answerKey && !storedAnswerKeyId)) {
      toast({
        title: 'Missing Information',
        description: 'Please load or process an answer sheet AND provide an answer key (upload or load stored).',
        variant: 'destructive',
      });
      return;
    }

    setIsProcessing(true);

    try {
      // 1. Resolve Answer Key ID — use stored if already loaded, else upload new
      let answerKeyId: number | null = storedAnswerKeyId;

      if (!answerKeyId && answerKey) {
        const keyFormData = new FormData();
        keyFormData.append('file', answerKey);
        const keyResponse = await api.post('/upload-answer-key', keyFormData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        answerKeyId = keyResponse.data.answer_key_id;
      }

      if (!answerKeyId) {
        toast({ title: 'Answer Key Error', description: 'No answer key available. Upload a file or load stored key.', variant: 'destructive' });
        setIsProcessing(false);
        return;
      }

      // 2. Call Backend Evaluation
      const evalFormData = new FormData();
      evalFormData.append('answer_sheet_id', answerSheetId.toString());
      evalFormData.append('answer_key_id', answerKeyId.toString());

      const response = await api.post('/evaluate', evalFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const result = response.data;

      // 3. Build evaluationData using actual marks from API (e.g., 18.5/50 not 100)
      const rawMaxMarks   = result.max_marks   ?? 50;
      const rawTotalMarks = result.total_marks  ?? Math.round(result.score * rawMaxMarks);
      const percentage    = result.percentage   ?? Math.round(result.score * 100);

      const questions = [];
      if (result.question_details && Object.keys(result.question_details).length > 0) {
        Object.entries(result.question_details)
          .sort(([a], [b]) => parseInt(a) - parseInt(b))
          .forEach(([qNum, details]: [string, any]) => {
            questions.push({
              number: parseInt(qNum),
              answer: `Question ${qNum} Response (See feedback for details)`,
              marks: details.marks_obtained,
              maxMarks: details.max_marks
            });
          });
      } else {
        questions.push({
          number: 1,
          answer: extractedText.substring(0, 200) + (extractedText.length > 200 ? "..." : ""),
          marks: rawTotalMarks,
          maxMarks: rawMaxMarks
        });
      }

      let grade = 'F';
      if (result.score >= 0.9) grade = 'A+';
      else if (result.score >= 0.8) grade = 'A';
      else if (result.score >= 0.7) grade = 'B';
      else if (result.score >= 0.5) grade = 'C';
      else if (result.score >= 0.4) grade = 'D';

      const evaluationData = {
        questions,
        totalMarks: rawTotalMarks,
        maxTotalMarks: rawMaxMarks,
        percentage: percentage,
        grade: grade,
        feedback: result.feedback ?? ''
      };

      // 4. Navigate to Result
      navigate(`/teacher/class/${classId}/result/${studentId}`, {
        state: {
          student,
          evaluationData
        }
      });

    } catch (error: any) {
      console.error("Evaluation Error:", error);
      toast({
        title: "Evaluation Failed",
        description: error.response?.data?.detail || "Could not complete evaluation.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-6xl">
          {/* Header */}
          <div className="mb-8 animate-fade-in">
            <Button
              variant="ghost"
              onClick={() => navigate(`/teacher/class/${classId}`)}
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Class {classId}
            </Button>

            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">Evaluate Answer Sheet</h1>
              {isReEvaluateMode && (
                <span className="bg-amber-500/20 text-amber-600 border border-amber-500/30 px-3 py-1 rounded-full text-sm font-semibold">
                  Re-Evaluation Mode
                </span>
              )}
            </div>
            {student && (
              <p className="text-muted-foreground">
                Student: {student.name} (Roll: {student.rollNumber})
              </p>
            )}
          </div>

          {/* Main Content Grid */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Section: Upload Cards */}
            <div className="space-y-6">
              <Card className="shadow-soft animate-fade-in-up">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Upload className="h-5 w-5 text-primary" />
                      Student Answer Sheet
                    </span>
                    {answerSheet && (
                      <Button variant="ghost" size="sm" onClick={clearAnswerSheet}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Upload student answer sheet for evaluation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!answerSheet ? (
                    <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-base cursor-pointer">
                      <Input
                        id="answerSheet"
                        type="file"
                        accept="image/*,.pdf"
                        onChange={handleAnswerSheetUpload}
                        className="hidden"
                      />
                      <label htmlFor="answerSheet" className="cursor-pointer">
                        <Upload className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                        <p className="text-sm font-medium mb-1">Upload Answer Sheet</p>
                        <p className="text-xs text-muted-foreground">
                          PNG, JPG, or PDF (max 10MB)
                        </p>
                      </label>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 text-sm">
                        <FileText className="h-4 w-4 text-primary" />
                        <span className="font-medium truncate">{answerSheet.name}</span>
                      </div>
                      {answerSheetPreview && (
                        <div className="border rounded-lg overflow-hidden bg-muted/30">
                          <img
                            src={answerSheetPreview}
                            alt="Answer Sheet Preview"
                            className="w-full h-auto max-h-64 object-contain"
                          />
                        </div>
                      )}
                      <Button
                        onClick={handleProcessOCR}
                        disabled={isProcessing}
                        className="w-full"
                      >
                        <ScanText className="h-4 w-4 mr-2" />
                        {isProcessing ? 'Processing OCR...' : 'Process with OCR'}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={loadStoredOCR}
                        disabled={isProcessing}
                        className="w-full text-xs"
                      >
                        ↩ Load Stored OCR
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="shadow-soft animate-fade-in-up" style={{ animationDelay: '100ms' }}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      Sample Answer Key
                    </span>
                    {answerKey && (
                      <Button variant="ghost" size="sm" onClick={clearAnswerKey}>
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Upload the correct answer key
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!answerKey && !storedAnswerKeyId ? (
                    <div className="space-y-3">
                      <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition-base cursor-pointer">
                        <Input
                          id="answerKey"
                          type="file"
                          accept="image/*,.pdf,.txt"
                          onChange={handleAnswerKeyUpload}
                          className="hidden"
                        />
                        <label htmlFor="answerKey" className="cursor-pointer">
                          <Upload className="h-10 w-10 mx-auto mb-2 text-muted-foreground" />
                          <p className="text-sm font-medium mb-1">Upload New Answer Key</p>
                          <p className="text-xs text-muted-foreground">PNG, JPG, PDF, or TXT</p>
                        </label>
                      </div>
                      <Button
                        variant="outline"
                        onClick={loadStoredKey}
                        disabled={isProcessing}
                        className="w-full text-xs"
                      >
                        ↩ Use Stored Answer Key
                      </Button>
                    </div>
                  ) : storedAnswerKeyId ? (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                        <FileText className="h-4 w-4 text-green-600" />
                        <span className="font-medium text-green-700 dark:text-green-400 truncate">
                          Stored: {storedKeyFilename} (ID: {storedAnswerKeyId})
                        </span>
                      </div>
                      <Button variant="ghost" size="sm" onClick={clearAnswerKey} className="w-full text-xs">
                        Clear & Upload New Key
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 text-sm">
                        <FileText className="h-4 w-4 text-primary" />
                        <span className="font-medium truncate">{answerKey.name}</span>
                      </div>
                      {answerKeyPreview && (
                        <div className="border rounded-lg overflow-hidden bg-muted/30 max-h-32">
                          <img
                            src={answerKeyPreview}
                            alt="Answer Key Preview"
                            className="w-full h-auto object-contain"
                          />
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right Section: Extracted Text Display */}
            <Card className="shadow-soft animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ScanText className="h-5 w-5 text-primary" />
                  Extracted Text
                </CardTitle>
                <CardDescription>
                  OCR extracted text from answer sheet
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border rounded-lg bg-muted/30 p-4 min-h-[400px] max-h-[400px] overflow-y-auto">
                  {extractedText ? (
                    <pre className="text-sm whitespace-pre-wrap font-mono text-foreground">
                      {extractedText}
                    </pre>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                      <ScanText className="h-16 w-16 mb-4 opacity-20" />
                      <p className="text-sm">No text extracted yet</p>
                      <p className="text-xs mt-2">Upload an answer sheet and process with OCR</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Evaluate Button */}
          <div className="mt-8 flex justify-center gap-4 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
            <Button
              size="lg"
              onClick={handleEvaluate}
              disabled={isProcessing || !answerSheetId || (!answerKey && !storedAnswerKeyId)}
              className="px-12"
            >
              {isProcessing ? 'Evaluating...' : 'Evaluate Answers'}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TeacherEvaluation;
