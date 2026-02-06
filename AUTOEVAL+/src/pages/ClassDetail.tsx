import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ClassroomService, Student } from '@/services/ClassroomService';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, UserPlus, Users, CheckCircle, Clock, GraduationCap } from 'lucide-react';
import { toast } from '@/hooks/use-toast';



const ClassDetail = () => {
  const { classId } = useParams();
  const navigate = useNavigate();

  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string>('');
  const [newStudentName, setNewStudentName] = useState('');
  const [newStudentRoll, setNewStudentRoll] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  // Fetch students on mount
  useEffect(() => {
    const fetchStudents = async () => {
      if (!classId) return;
      try {
        const data = await ClassroomService.getStudents(classId);
        setStudents(data);
      } catch (error) {
        toast({ title: "Error", description: "Failed to load students", variant: "destructive" });
      }
    };
    fetchStudents();
  }, [classId]);

  const handleAddStudent = async () => {
    if (!newStudentName.trim() || !newStudentRoll.trim()) {
      toast({
        title: "Missing Information",
        description: "Please enter both student name and roll number.",
        variant: "destructive",
      });
      return;
    }

    if (!classId) return;

    try {
      const newStudent = await ClassroomService.addStudent(classId, newStudentName, newStudentRoll);
      setStudents(prev => [...prev, newStudent]);
      setNewStudentName('');
      setNewStudentRoll('');
      setShowAddForm(false);

      toast({
        title: "Student Added",
        description: `${newStudent.name} has been added to Class ${classId}.`,
      });
    } catch (error) {
      toast({ title: "Error", description: "Failed to add student. Check backend logs.", variant: "destructive" });
    }
  };

  const handleSelectStudent = (studentId: string) => {
    setSelectedStudent(studentId);
  };

  const handleProceedToEvaluation = () => {
    if (!selectedStudent) {
      toast({
        title: "No Student Selected",
        description: "Please select a student to evaluate.",
        variant: "destructive",
      });
      return;
    }

    const student = students.find(s => String(s.id) === selectedStudent);
    navigate(`/teacher/class/${classId}/evaluate/${selectedStudent}`, {
      state: { student }
    });
  };

  const pendingStudents = students.filter(s => !s.evaluated);
  const evaluatedStudents = students.filter(s => s.evaluated);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-5xl">
          {/* Header */}
          <div className="mb-8 animate-fade-in">
            <Button
              variant="ghost"
              onClick={() => navigate('/teacher-dashboard')}
              className="mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Classes
            </Button>

            <div className="flex items-center gap-3">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-light">
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Class {classId}</h1>
                <p className="text-muted-foreground">
                  {students.length} students • {evaluatedStudents.length} evaluated
                </p>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column: Student Selection & Add */}
            <div className="space-y-6">
              {/* Student Selection */}
              <Card className="shadow-soft animate-fade-in-up">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-primary" />
                    Select Student
                  </CardTitle>
                  <CardDescription>
                    Choose a student to evaluate their answer sheet
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Select value={selectedStudent} onValueChange={handleSelectStudent}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a student..." />
                    </SelectTrigger>
                    <SelectContent className="bg-popover border shadow-lg z-50">
                      {students.length === 0 ? (
                        <div className="px-4 py-3 text-sm text-muted-foreground">
                          No students added yet
                        </div>
                      ) : (
                        students.map(student => (
                          <SelectItem
                            key={student.id}
                            value={String(student.id)}
                            className="cursor-pointer"
                          >
                            <div className="flex items-center gap-2">
                              <span>{student.name} ({student.rollNumber})</span>
                              {student.evaluated && (
                                <Badge variant="secondary" className="bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Checked
                                </Badge>
                              )}
                              {!student.evaluated && (
                                <Badge variant="outline" className="text-amber-600 border-amber-300">
                                  <Clock className="h-3 w-3 mr-1" />
                                  Pending
                                </Badge>
                              )}
                            </div>
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>

                  <Button
                    onClick={handleProceedToEvaluation}
                    disabled={!selectedStudent}
                    className="w-full"
                  >
                    Proceed to Evaluation
                  </Button>
                </CardContent>
              </Card>

              {/* Add Student */}
              <Card className="shadow-soft animate-fade-in-up" style={{ animationDelay: '100ms' }}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserPlus className="h-5 w-5 text-primary" />
                    Add Student
                  </CardTitle>
                  <CardDescription>
                    Add a new student to this class
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!showAddForm ? (
                    <Button
                      variant="outline"
                      onClick={() => setShowAddForm(true)}
                      className="w-full"
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Add New Student
                    </Button>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="studentName">Student Name</Label>
                        <Input
                          id="studentName"
                          placeholder="Enter student name"
                          value={newStudentName}
                          onChange={(e) => setNewStudentName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="rollNumber">Roll Number</Label>
                        <Input
                          id="rollNumber"
                          placeholder="Enter roll number"
                          value={newStudentRoll}
                          onChange={(e) => setNewStudentRoll(e.target.value)}
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button onClick={handleAddStudent} className="flex-1">
                          Add Student
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowAddForm(false);
                            setNewStudentName('');
                            setNewStudentRoll('');
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right Column: Evaluated Students */}
            <Card className="shadow-soft animate-fade-in-up h-fit" style={{ animationDelay: '200ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  Evaluated Students
                </CardTitle>
                <CardDescription>
                  Students who have been evaluated
                </CardDescription>
              </CardHeader>
              <CardContent>
                {evaluatedStudents.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <CheckCircle className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p className="text-sm">No evaluations completed yet</p>
                    <p className="text-xs mt-2">
                      Select a student and complete an evaluation
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto">
                    {evaluatedStudents.map(student => (
                      <div
                        key={student.id}
                        className="flex items-center justify-between p-4 rounded-lg bg-muted/50 border"
                      >
                        <div>
                          <p className="font-medium">{student.name}</p>
                          <p className="text-sm text-muted-foreground">
                            Roll: {student.rollNumber}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">{student.marks}/100</p>
                          <Badge className="bg-primary text-primary-foreground">
                            {student.grade}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Pending Students Overview */}
          {pendingStudents.length > 0 && (
            <Card className="mt-8 shadow-soft animate-fade-in-up" style={{ animationDelay: '300ms' }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-amber-500" />
                  Pending Evaluations
                </CardTitle>
                <CardDescription>
                  {pendingStudents.length} student(s) awaiting evaluation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {pendingStudents.map(student => (
                    <Badge
                      key={student.id}
                      variant="outline"
                      className="cursor-pointer hover:bg-muted"
                      onClick={() => setSelectedStudent(String(student.id))}
                    >
                      {student.name} ({student.rollNumber})
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default ClassDetail;
