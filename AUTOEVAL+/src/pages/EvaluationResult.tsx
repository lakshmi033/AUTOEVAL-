import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, CheckCircle, FileText, Award, MessageSquare } from 'lucide-react';

interface QuestionResult {
  number: number;
  answer: string;
  marks: number;
  maxMarks: number;
}

interface EvaluationData {
  questions: QuestionResult[];
  totalMarks: number;
  maxTotalMarks: number;
  grade: string;
  feedback: string;
}

interface LocationState {
  student?: {
    id: string;
    name: string;
    rollNumber: string;
  };
  evaluationData?: EvaluationData;
}

const EvaluationResult = () => {
  const { classId, studentId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { student, evaluationData } = (location.state as LocationState) || {};

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return 'bg-green-500 text-white';
      case 'B+':
      case 'B':
        return 'bg-blue-500 text-white';
      case 'C+':
      case 'C':
        return 'bg-amber-500 text-white';
      case 'D':
        return 'bg-orange-500 text-white';
      default:
        return 'bg-red-500 text-white';
    }
  };

  const getMarkColor = (marks: number, maxMarks: number) => {
    const percentage = (marks / maxMarks) * 100;
    if (percentage >= 90) return 'text-green-600 dark:text-green-400';
    if (percentage >= 70) return 'text-blue-600 dark:text-blue-400';
    if (percentage >= 50) return 'text-amber-600 dark:text-amber-400';
    return 'text-red-600 dark:text-red-400';
  };

  if (!evaluationData) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="pt-24 pb-12 px-4">
          <div className="container mx-auto max-w-4xl text-center">
            <h1 className="text-2xl font-bold mb-4">No Evaluation Data</h1>
            <p className="text-muted-foreground mb-8">
              Please complete an evaluation first.
            </p>
            <Button onClick={() => navigate(`/teacher/class/${classId}`)}>
              Back to Class
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
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

            <div className="flex items-center gap-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-light">
                <CheckCircle className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Evaluation Result</h1>
                {student && (
                  <p className="text-muted-foreground">
                    {student.name} (Roll: {student.rollNumber})
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Summary Card */}
          <Card className="shadow-soft mb-8 animate-fade-in-up">
            <CardContent className="pt-6">
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div>
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light mb-3">
                    <FileText className="h-8 w-8 text-primary" />
                  </div>
                  <p className="text-3xl font-bold">
                    {evaluationData.totalMarks}/{evaluationData.maxTotalMarks}
                  </p>
                  <p className="text-sm text-muted-foreground">Total Marks</p>
                </div>

                <div>
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light mb-3">
                    <Award className="h-8 w-8 text-primary" />
                  </div>
                  <Badge className={`text-2xl px-4 py-2 ${getGradeColor(evaluationData.grade)}`}>
                    {evaluationData.grade}
                  </Badge>
                  <p className="text-sm text-muted-foreground mt-2">Grade</p>
                </div>

                <div>
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light mb-3">
                    <CheckCircle className="h-8 w-8 text-primary" />
                  </div>
                  <p className="text-3xl font-bold">
                    {Math.round((evaluationData.totalMarks / evaluationData.maxTotalMarks) * 100)}%
                  </p>
                  <p className="text-sm text-muted-foreground">Percentage</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Question-wise Results */}
          <Card className="shadow-soft mb-8 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Question-wise Results
              </CardTitle>
              <CardDescription>
                Detailed breakdown of marks for each question
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {evaluationData.questions.map((question, index) => (
                  <div key={question.number}>
                    <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/30">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary-light flex items-center justify-center">
                        <span className="font-bold text-primary">Q{question.number}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-foreground leading-relaxed">
                          {question.answer}
                        </p>
                      </div>
                      <div className="flex-shrink-0 text-right">
                        <p className={`text-lg font-bold ${getMarkColor(question.marks, question.maxMarks)}`}>
                          {question.marks}/{question.maxMarks}
                        </p>
                      </div>
                    </div>
                    {index < evaluationData.questions.length - 1 && (
                      <Separator className="my-2" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Feedback Section */}
          <Card className="shadow-soft animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                Feedback
              </CardTitle>
              <CardDescription>
                Overall evaluation feedback
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-muted/30 border">
                <p className="text-foreground leading-relaxed whitespace-pre-wrap font-mono text-sm">
                  {evaluationData.feedback}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="mt-8 flex justify-center gap-4 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
            <Button
              variant="outline"
              onClick={() => navigate(`/teacher/class/${classId}`)}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Class
            </Button>
            <Button onClick={() => navigate('/teacher-dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EvaluationResult;
