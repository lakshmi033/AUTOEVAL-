import { useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { GraduationCap, BookOpen, FileText, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { useEffect } from 'react';

interface QuestionResult {
  questionNumber: number;
  studentAnswer: string;
  marks: number;
  maxMarks: number;
}

const StudentDashboard = () => {
  const { user } = useAuth();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch real results on mount
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await api.get('/student/results');
        setResults(response.data);
      } catch (error) {
        console.error("Failed to fetch results", error);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, []);

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
              View your evaluation results below.
            </p>
          </div>

          {/* Real Results Section */}
          <div className="animate-fade-in" style={{ animationDelay: '200ms' }}>
            <h2 className="text-xl font-semibold mb-4">Your Recent Evaluations</h2>

            {results.length === 0 ? (
              <Card className="shadow-sm">
                <CardContent className="py-16">
                  <div className="flex flex-col items-center justify-center text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                      <Clock className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">No Results Yet</h3>
                    <p className="text-muted-foreground max-w-md">
                      You haven't received any evaluations yet. Once your teacher evaluates your answer sheets, they will appear here.
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {results.map((result: any) => (
                  <Card key={result.id} className="shadow-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-500" />
                          {result.test_name}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {new Date(result.created_at).toLocaleDateString()}
                        </span>
                      </CardTitle>
                      <CardDescription>
                        {result.subject}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid sm:grid-cols-2 gap-6">
                        <div className="p-4 rounded-lg bg-muted/50 text-center">
                          <p className="text-sm text-muted-foreground mb-1">Score</p>
                          <p className="text-3xl font-bold text-primary">
                            {Math.round(result.score * 100)}%
                          </p>
                        </div>
                        <div className="p-4 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Feedback</p>
                          <p className="text-sm italic">"{result.feedback}"</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>


        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
