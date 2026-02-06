import { useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { GraduationCap, BookOpen, FileText, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface QuestionResult {
  questionNumber: number;
  studentAnswer: string;
  marks: number;
  maxMarks: number;
}

interface EvaluationResult {
  subject: string;
  testName: string;
  isPublished: boolean;
  questions: QuestionResult[];
  totalMarks: number;
  maxTotalMarks: number;
  grade: string;
  feedback: string;
}

// Simulated results data - will be fetched from backend later
const mockResults: Record<string, Record<string, EvaluationResult | null>> = {
  'Mathematics': {
    'Internal 1': {
      subject: 'Mathematics',
      testName: 'Internal 1',
      isPublished: true,
      questions: [
        { questionNumber: 1, studentAnswer: 'The derivative of x² is 2x using the power rule.', marks: 5, maxMarks: 5 },
        { questionNumber: 2, studentAnswer: 'Integration is the reverse of differentiation.', marks: 4, maxMarks: 5 },
        { questionNumber: 3, studentAnswer: 'The limit of f(x) as x approaches 0 is calculated using L\'Hopital\'s rule.', marks: 4, maxMarks: 5 },
        { questionNumber: 4, studentAnswer: 'Matrix multiplication is not commutative.', marks: 5, maxMarks: 5 },
        { questionNumber: 5, studentAnswer: 'Eigenvalues are found by solving det(A - λI) = 0.', marks: 3, maxMarks: 5 },
      ],
      totalMarks: 21,
      maxTotalMarks: 25,
      grade: 'A',
      feedback: 'Excellent understanding of calculus concepts. Good grasp of linear algebra. Minor errors in eigenvalue calculation. Keep up the good work!'
    },
    'Internal 2': null,
    'Internal 3': null,
  },
  'Physics': {
    'Internal 1': {
      subject: 'Physics',
      testName: 'Internal 1',
      isPublished: true,
      questions: [
        { questionNumber: 1, studentAnswer: 'Newton\'s first law states that an object at rest stays at rest.', marks: 4, maxMarks: 5 },
        { questionNumber: 2, studentAnswer: 'F = ma is Newton\'s second law of motion.', marks: 5, maxMarks: 5 },
        { questionNumber: 3, studentAnswer: 'Energy cannot be created or destroyed, only transformed.', marks: 5, maxMarks: 5 },
        { questionNumber: 4, studentAnswer: 'The speed of light is approximately 3 × 10^8 m/s.', marks: 5, maxMarks: 5 },
      ],
      totalMarks: 19,
      maxTotalMarks: 20,
      grade: 'A+',
      feedback: 'Outstanding performance! Clear understanding of fundamental physics concepts. Excellent precision in answers.'
    },
    'Internal 2': null,
    'Internal 3': null,
  },
  'Chemistry': {
    'Internal 1': null,
    'Internal 2': null,
    'Internal 3': null,
  },
  'Computer Science': {
    'Internal 1': {
      subject: 'Computer Science',
      testName: 'Internal 1',
      isPublished: true,
      questions: [
        { questionNumber: 1, studentAnswer: 'An algorithm is a step-by-step procedure for solving a problem.', marks: 5, maxMarks: 5 },
        { questionNumber: 2, studentAnswer: 'Big O notation describes the upper bound of time complexity.', marks: 4, maxMarks: 5 },
        { questionNumber: 3, studentAnswer: 'A stack is a LIFO data structure.', marks: 5, maxMarks: 5 },
        { questionNumber: 4, studentAnswer: 'Binary search has O(log n) time complexity.', marks: 5, maxMarks: 5 },
        { questionNumber: 5, studentAnswer: 'Recursion is when a function calls itself.', marks: 4, maxMarks: 5 },
      ],
      totalMarks: 23,
      maxTotalMarks: 25,
      grade: 'A',
      feedback: 'Very good understanding of data structures and algorithms. Solid grasp of complexity analysis. Continue practicing problem-solving!'
    },
    'Internal 2': null,
    'Internal 3': null,
  },
};

const subjects = ['Mathematics', 'Physics', 'Chemistry', 'Computer Science'];
const tests = ['Internal 1', 'Internal 2', 'Internal 3'];

const StudentDashboard = () => {
  const { user } = useAuth();
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedTest, setSelectedTest] = useState<string>('');

  const getResult = (): EvaluationResult | null => {
    if (!selectedSubject || !selectedTest) return null;
    return mockResults[selectedSubject]?.[selectedTest] || null;
  };

  const result = getResult();

  const getGradeColor = (grade: string) => {
    if (grade === 'A+' || grade === 'A') return 'text-green-600 dark:text-green-400';
    if (grade === 'B+' || grade === 'B') return 'text-blue-600 dark:text-blue-400';
    if (grade === 'C+' || grade === 'C') return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          {/* Welcome Section */}
          <div className="mb-10 animate-fade-in">
            <div className="flex items-center gap-3 mb-2">
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                <GraduationCap className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">
                  Welcome, {user?.username || 'Student'}!
                </h1>
                {user?.rollNumber && (
                  <p className="text-sm text-muted-foreground">Roll Number: {user.rollNumber}</p>
                )}
              </div>
            </div>
            <p className="text-lg text-muted-foreground mt-2">
              View your evaluation results
            </p>
          </div>

          {/* Selection Section */}
          <Card className="shadow-sm mb-8 animate-fade-in" style={{ animationDelay: '100ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                Select Subject & Test
              </CardTitle>
              <CardDescription>
                Choose a subject and internal test to view your results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Subject</label>
                  <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select subject" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects.map((subject) => (
                        <SelectItem key={subject} value={subject}>
                          {subject}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Internal Test</label>
                  <Select value={selectedTest} onValueChange={setSelectedTest}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select test" />
                    </SelectTrigger>
                    <SelectContent>
                      {tests.map((test) => (
                        <SelectItem key={test} value={test}>
                          {test}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Results Section */}
          {selectedSubject && selectedTest && (
            <div className="animate-fade-in" style={{ animationDelay: '200ms' }}>
              {result && result.isPublished ? (
                <>
                  {/* Summary Card */}
                  <Card className="shadow-sm mb-6">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Evaluation Results
                      </CardTitle>
                      <CardDescription>
                        {result.subject} - {result.testName}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid sm:grid-cols-3 gap-6 text-center">
                        <div className="p-4 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Total Marks</p>
                          <p className="text-3xl font-bold text-primary">
                            {result.totalMarks}/{result.maxTotalMarks}
                          </p>
                        </div>
                        <div className="p-4 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Percentage</p>
                          <p className="text-3xl font-bold text-primary">
                            {Math.round((result.totalMarks / result.maxTotalMarks) * 100)}%
                          </p>
                        </div>
                        <div className="p-4 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Grade</p>
                          <p className={`text-3xl font-bold ${getGradeColor(result.grade)}`}>
                            {result.grade}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Question-wise Results */}
                  <Card className="shadow-sm mb-6">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-primary" />
                        Question-wise Marks
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {result.questions.map((q, index) => (
                          <div key={q.questionNumber}>
                            <div className="flex items-start justify-between gap-4 py-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-sm font-medium">
                                    {q.questionNumber}
                                  </span>
                                  <span className="font-medium">Question {q.questionNumber}</span>
                                </div>
                                <p className="text-sm text-muted-foreground pl-8">
                                  {q.studentAnswer}
                                </p>
                              </div>
                              <div className="text-right">
                                <span className={`text-lg font-bold ${q.marks === q.maxMarks ? 'text-green-600 dark:text-green-400' : q.marks >= q.maxMarks * 0.5 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'}`}>
                                  {q.marks}/{q.maxMarks}
                                </span>
                              </div>
                            </div>
                            {index < result.questions.length - 1 && <Separator />}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Feedback Card */}
                  <Card className="shadow-sm">
                    <CardHeader>
                      <CardTitle>Teacher's Feedback</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground leading-relaxed">
                        {result.feedback}
                      </p>
                    </CardContent>
                  </Card>
                </>
              ) : (
                <Card className="shadow-sm">
                  <CardContent className="py-16">
                    <div className="flex flex-col items-center justify-center text-center">
                      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                        <Clock className="h-8 w-8 text-muted-foreground" />
                      </div>
                      <h3 className="text-xl font-semibold mb-2">Results Not Published Yet</h3>
                      <p className="text-muted-foreground max-w-md">
                        The evaluation for {selectedSubject} - {selectedTest} has not been completed yet. 
                        Please check back later once your teacher has published the results.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Initial State - No Selection */}
          {(!selectedSubject || !selectedTest) && (
            <Card className="shadow-sm animate-fade-in" style={{ animationDelay: '200ms' }}>
              <CardContent className="py-16">
                <div className="flex flex-col items-center justify-center text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                    <AlertCircle className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Select Subject & Test</h3>
                  <p className="text-muted-foreground max-w-md">
                    Please select a subject and internal test from the dropdowns above to view your evaluation results.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
