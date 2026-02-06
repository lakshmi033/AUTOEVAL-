import { useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Upload, FileText, ScanText, X } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

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
    
    setTimeout(() => {
      setIsProcessing(false);
      setExtractedText(
        "Q1: The mitochondria is the powerhouse of the cell. It produces ATP through cellular respiration.\n\n" +
        "Q2: Photosynthesis is the process by which plants convert light energy into chemical energy.\n\n" +
        "Q3: DNA stands for Deoxyribonucleic acid and contains genetic instructions.\n\n" +
        "Q4: The water cycle involves evaporation, condensation, and precipitation.\n\n" +
        "Q5: Newton's first law states that an object at rest stays at rest unless acted upon by an external force.\n\n" +
        "[Note: This is simulated OCR output. Real OCR will be integrated with backend.]"
      );
      toast({
        title: "OCR Processing Complete",
        description: "Text has been extracted from the answer sheet.",
      });
    }, 2000);
  };

  const handleEvaluate = async () => {
    if (!answerSheet || !answerKey) {
      toast({
        title: "Missing Information",
        description: "Please upload both answer sheet and answer key.",
        variant: "destructive",
      });
      return;
    }

    if (!extractedText) {
      toast({
        title: "Process OCR First",
        description: "Please process the answer sheet with OCR before evaluation.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    
    // Simulate evaluation processing
    setTimeout(() => {
      setIsProcessing(false);
      
      // Navigate to result page with evaluation data
      navigate(`/teacher/class/${classId}/result/${studentId}`, {
        state: {
          student,
          evaluationData: {
            questions: [
              { number: 1, answer: "The mitochondria is the powerhouse of the cell. It produces ATP through cellular respiration.", marks: 8, maxMarks: 10 },
              { number: 2, answer: "Photosynthesis is the process by which plants convert light energy into chemical energy.", marks: 10, maxMarks: 10 },
              { number: 3, answer: "DNA stands for Deoxyribonucleic acid and contains genetic instructions.", marks: 9, maxMarks: 10 },
              { number: 4, answer: "The water cycle involves evaporation, condensation, and precipitation.", marks: 7, maxMarks: 10 },
              { number: 5, answer: "Newton's first law states that an object at rest stays at rest unless acted upon by an external force.", marks: 10, maxMarks: 10 },
            ],
            totalMarks: 44,
            maxTotalMarks: 50,
            grade: 'A',
            feedback: 'Excellent understanding of the concepts. Minor improvements needed in Q1 and Q4. Keep up the good work!'
          }
        }
      });
    }, 2000);
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
              disabled={isProcessing || !extractedText || !answerKey}
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
