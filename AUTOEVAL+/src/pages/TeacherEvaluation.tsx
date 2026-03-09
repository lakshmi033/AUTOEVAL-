import { useState } from 'react';
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
}

const TeacherEvaluation = () => {
  const { classId, studentId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { student } = (location.state as LocationState) || {};

  const [answerSheet, setAnswerSheet] = useState<File | null>(null);
  const [answerSheetPreview, setAnswerSheetPreview] = useState<string | null>(null);
  const [answerKey, setAnswerKey] = useState<File | null>(null);
  const [answerKeyPreview, setAnswerKeyPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [answerSheetId, setAnswerSheetId] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

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
  };

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
    if (!answerSheetId || !answerKey) {
      toast({
        title: "Missing Information",
        description: "Please process the answer sheet first and upload an answer key.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);

    try {
      // 1. Upload Answer Key to DB
      const keyFormData = new FormData();
      keyFormData.append('file', answerKey);

      const keyResponse = await api.post('/upload-answer-key', keyFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const answerKeyId = keyResponse.data.answer_key_id;

      if (!answerKeyId) {
        toast({ title: "Answer Key Error", description: "Failed to upload answer key.", variant: "destructive" });
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

      // 3. Map Result to Frontend Structure
      // Note: Backend gives a holistic score [0-1]. We map this to a single "Comprehensive" question.
      const maxMarks = 100;
      const obtainedMarks = Math.round(result.score * maxMarks);
      let grade = 'F';
      if (result.score >= 0.9) grade = 'A+';
      else if (result.score >= 0.8) grade = 'A';
      else if (result.score >= 0.7) grade = 'B';
      else if (result.score >= 0.6) grade = 'C';
      else if (result.score >= 0.5) grade = 'D';

      const evaluationData = {
        questions: [
          {
            number: 1,
            answer: extractedText.substring(0, 200) + (extractedText.length > 200 ? "..." : ""),
            marks: obtainedMarks,
            maxMarks: maxMarks
          }
        ],
        totalMarks: obtainedMarks,
        maxTotalMarks: maxMarks,
        grade: grade,
        feedback: result.feedback + (result.method ? ` (Method: ${result.method})` : "")
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

            <h1 className="text-3xl font-bold mb-2">Evaluate Answer Sheet</h1>
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
                  {!answerKey ? (
                    <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-base cursor-pointer">
                      <Input
                        id="answerKey"
                        type="file"
                        accept="image/*,.pdf,.txt"
                        onChange={handleAnswerKeyUpload}
                        className="hidden"
                      />
                      <label htmlFor="answerKey" className="cursor-pointer">
                        <Upload className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                        <p className="text-sm font-medium mb-1">Upload Answer Key</p>
                        <p className="text-xs text-muted-foreground">
                          PNG, JPG, PDF, or TXT
                        </p>
                      </label>
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
              disabled={isProcessing || !answerSheetId || !answerKey}
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
