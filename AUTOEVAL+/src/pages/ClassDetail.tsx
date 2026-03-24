import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ClassroomService, Student } from '@/services/ClassroomService';
import { api } from '@/lib/api';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, UserPlus, Users, CheckCircle, Clock, GraduationCap, Eye, FileText, BarChart3 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const ClassDetail = () => {
  const { classId } = useParams();
  const navigate = useNavigate();

  const [students, setStudents] = useState<Student[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'students' | 'evaluated' | 'pending'>('dashboard');
  const [selectedStudent, setSelectedStudent] = useState<string>('');
  const [newStudentName, setNewStudentName] = useState('');
  const [newStudentRoll, setNewStudentRoll] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  // View Result State
  const [selectedEval, setSelectedEval] = useState<any>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isLoadingEval, setIsLoadingEval] = useState(false);

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

  const handleViewResult = async (student: Student) => {
    setIsLoadingEval(true);
    setIsViewModalOpen(true);
    try {
      const evaluation = await ClassroomService.getLatestEvaluation(student.id);
      setSelectedEval({ ...evaluation, studentName: student.name });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load evaluation details.",
        variant: "destructive"
      });
      setIsViewModalOpen(false);
    } finally {
      setIsLoadingEval(false);
    }
  };

  const handleExportMarks = async () => {
    try {
      const response = await api.get('/teacher/export-marks', { responseType: 'blob' });
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // Get filename from content-disposition header if possible, otherwise use default
      const disposition = response.headers['content-disposition'];
      let filename = 'MarkList.xlsx';
      if (disposition && disposition.indexOf('attachment') !== -1) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          const matches = filenameRegex.exec(disposition);
          if (matches != null && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
          }
      }
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
       toast({
         title: "Export Failed",
         description: "Failed to download the mark list. Please check if you have evaluated students.",
         variant: "destructive"
       });
    }
  };

  const pendingStudents = students.filter(s => !s.evaluated);
  const evaluatedStudents = students.filter(s => s.evaluated);

  const NavItem = ({ id, label, icon: Icon }: { id: typeof activeTab, label: string, icon: any }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
        activeTab === id 
          ? 'bg-primary text-primary-foreground shadow-md' 
          : 'hover:bg-muted text-muted-foreground hover:text-foreground'
      }`}
    >
      <Icon className="h-5 w-5" />
      <span className="font-medium">{label}</span>
      {id === 'pending' && pendingStudents.length > 0 && (
        <span className="ml-auto bg-amber-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">
          {pendingStudents.length}
        </span>
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />

      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-6xl">
          {/* Top Bar / Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/teacher-dashboard')}
                className="rounded-full"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                  <GraduationCap className="h-8 w-8 text-primary" />
                  Class {classId}
                </h1>
                <p className="text-muted-foreground text-sm">
                  Management Dashboard for {students.length} Students
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
               <Badge variant="outline" className="px-3 py-1 bg-green-500/5 text-green-600 border-green-500/20">
                 <CheckCircle className="h-3 w-3 mr-2" />
                 {evaluatedStudents.length} Evaluated
               </Badge>
               <Badge variant="outline" className="px-3 py-1 bg-amber-500/5 text-amber-600 border-amber-500/20">
                 <Clock className="h-3 w-3 mr-2" />
                 {pendingStudents.length} Pending
               </Badge>
               <Button onClick={handleExportMarks} variant="outline" size="sm" className="ml-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200">
                 <FileText className="h-4 w-4 mr-2" />
                 Export Mark List
               </Button>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-8">
            {/* LEFT SIDEBAR NAVIGATION */}
            <aside className="w-full lg:w-64 space-y-2">
              <NavItem id="dashboard" label="Dashboard" icon={GraduationCap} />
              <NavItem id="students" label="Student List" icon={Users} />
              <NavItem id="evaluated" label="Evaluated" icon={CheckCircle} />
              <NavItem id="pending" label="Pending" icon={Clock} />
            </aside>

            {/* RIGHT CONTENT AREA */}
            <div className="flex-1 animate-fade-in">
              
              {/* 📊 DASHBOARD VIEW */}
              {activeTab === 'dashboard' && (
                <div className="space-y-6">
                  <div className="grid sm:grid-cols-3 gap-4">
                    <Card className="bg-primary/5 border-primary/20 shadow-sm">
                      <CardHeader className="pb-2">
                        <CardDescription>Total Students</CardDescription>
                        <CardTitle className="text-3xl font-bold">{students.length}</CardTitle>
                      </CardHeader>
                    </Card>
                    <Card className="bg-green-500/5 border-green-500/20 shadow-sm">
                      <CardHeader className="pb-2">
                        <CardDescription>Evaluated</CardDescription>
                        <CardTitle className="text-3xl font-bold text-green-600">{evaluatedStudents.length}</CardTitle>
                      </CardHeader>
                    </Card>
                    <Card className="bg-amber-500/5 border-amber-500/20 shadow-sm">
                      <CardHeader className="pb-2">
                        <CardDescription>Pending</CardDescription>
                        <CardTitle className="text-3xl font-bold text-amber-600">{pendingStudents.length}</CardTitle>
                      </CardHeader>
                    </Card>
                  </div>

                  <Card className="overflow-hidden">
                    <div className="h-2 w-full bg-muted">
                        <div 
                          className="h-full bg-primary transition-all duration-500" 
                          style={{ width: `${students.length > 0 ? (evaluatedStudents.length / students.length) * 100 : 0}%` }}
                        />
                    </div>
                    <CardHeader>
                      <CardTitle className="text-lg">Class Progress</CardTitle>
                      <CardDescription>
                        {Math.round(students.length > 0 ? (evaluatedStudents.length / students.length) * 100 : 0)}% of evaluations completed for this class.
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button variant="outline" className="w-full" onClick={() => setActiveTab('students')}>
                        Go to Evaluation Menu
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* 👥 STUDENT LIST VIEW */}
              {activeTab === 'students' && (
                <div className="grid md:grid-cols-2 gap-6">
                   <Card className="shadow-soft">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Users className="h-5 w-5 text-primary" />
                          Proceed to Evaluation
                        </CardTitle>
                        <CardDescription>Select a student to start checking their answer sheet</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <Select value={selectedStudent} onValueChange={handleSelectStudent}>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select a student..." />
                          </SelectTrigger>
                          <SelectContent className="bg-popover border shadow-lg z-50">
                            {students.length === 0 ? (
                              <div className="px-4 py-3 text-sm text-muted-foreground">No students found</div>
                            ) : (
                              students.map(s => (
                                <SelectItem key={s.id} value={String(s.id)} className="cursor-pointer">
                                  {s.name} ({s.rollNumber}) {s.evaluated ? 'Evaluated' : 'Pending'}
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                        <Button onClick={handleProceedToEvaluation} disabled={!selectedStudent} className="w-full">
                          Start Evaluation
                        </Button>
                      </CardContent>
                   </Card>

                   <Card className="shadow-soft">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <UserPlus className="h-5 w-5 text-primary" />
                          Quick Add
                        </CardTitle>
                        <CardDescription>Add new student to Class {classId}</CardDescription>
                      </CardHeader>
                      <CardContent>
                         {!showAddForm ? (
                           <Button variant="outline" onClick={() => setShowAddForm(true)} className="w-full">
                             <UserPlus className="h-4 w-4 mr-2" /> Add Student
                           </Button>
                         ) : (
                           <div className="space-y-4">
                              <Input placeholder="Full Name" value={newStudentName} onChange={e => setNewStudentName(e.target.value)} />
                              <Input placeholder="Roll Number" value={newStudentRoll} onChange={e => setNewStudentRoll(e.target.value)} />
                              <div className="flex gap-2">
                                <Button onClick={handleAddStudent} className="flex-1">Add</Button>
                                <Button variant="ghost" onClick={() => setShowAddForm(false)}>Cancel</Button>
                              </div>
                           </div>
                         )}
                      </CardContent>
                   </Card>
                </div>
              )}

              {/* ✅ EVALUATED VIEW */}
              {activeTab === 'evaluated' && (
                <Card className="shadow-soft">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Evaluated Records
                    </CardTitle>
                    <CardDescription>Review marks and grades for checked papers</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {evaluatedStudents.length === 0 ? (
                      <div className="text-center py-12 text-muted-foreground">No students evaluated yet.</div>
                    ) : (
                      <div className="space-y-3">
                        {/* Header Row */}
                        <div className="grid grid-cols-7 px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider bg-muted/30 rounded-t-lg">
                          <div className="col-span-1">Student Name</div>
                          <div className="col-span-1">Subject</div>
                          <div className="col-span-1 text-center">Marks</div>
                          <div className="col-span-1 text-center">Grade</div>
                          <div className="col-span-1 text-center">Result</div>
                          <div className="col-span-2 text-right px-2">Actions</div>
                        </div>

                        {evaluatedStudents.map(s => (
                          <div key={s.id} className="grid grid-cols-7 items-center p-4 rounded-lg bg-muted/50 border hover:bg-muted transition-colors gap-4">
                            <div className="col-span-1">
                              <p className="font-semibold text-sm">{s.name}</p>
                              <p className="text-[10px] text-muted-foreground">Roll: {s.rollNumber}</p>
                            </div>
                            <div className="col-span-1 text-muted-foreground text-xs uppercase">
                              General
                            </div>
                            <div className="col-span-1 font-bold text-sm text-center">
                              {s.marks}/50
                            </div>
                            <div className="col-span-1 flex justify-center">
                              <Badge variant="outline" className="text-[10px] h-5 px-3">{s.grade}</Badge>
                            </div>
                            <div className="col-span-1 flex justify-center">
                               <Badge 
                                 className={`text-[10px] h-5 px-3 ${
                                   s.passStatus === 'PASS' 
                                     ? 'bg-green-500 hover:bg-green-600' 
                                     : 'bg-destructive hover:bg-destructive/90'
                                 }`}
                               >
                                 {s.passStatus}
                               </Badge>
                            </div>
                            <div className="col-span-2 flex justify-end gap-2 px-2">
                              <Button 
                                size="sm" 
                                variant="outline" 
                                className="h-8 text-xs gap-1 border-primary/20 hover:bg-primary/5 text-primary"
                                onClick={() => handleViewResult(s)}
                              >
                                <Eye className="h-3 w-3" /> View Result
                              </Button>
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                className="h-8 text-xs text-muted-foreground hover:text-foreground"
                                onClick={() => {
                                  navigate(`/teacher/class/${classId}/evaluate/${s.id}`, {
                                    state: { student: s, reEvaluate: true }
                                  });
                                }}
                              >
                                Re-Evaluate
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* ⏳ PENDING VIEW */}
              {activeTab === 'pending' && (
                <Card className="shadow-soft">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5 text-amber-500" />
                      Pending Evaluations
                    </CardTitle>
                    <CardDescription>Students awaiting assessment</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {pendingStudents.length === 0 ? (
                      <div className="text-center py-12 text-muted-foreground">All students have been evaluated.</div>
                    ) : (
                      <div className="grid gap-2">
                        {pendingStudents.map(s => (
                          <div
                            key={s.id}
                            onClick={() => {
                              setSelectedStudent(String(s.id));
                              setActiveTab('students');
                            }}
                            className="flex items-center gap-3 p-4 rounded-lg bg-amber-500/5 border border-amber-500/20 hover:bg-amber-500/10 cursor-pointer transition-colors"
                          >
                            <Clock className="h-4 w-4 text-amber-500" />
                            <span className="font-medium">{s.name}</span>
                            <span className="text-xs text-muted-foreground ml-auto">Roll: {s.rollNumber}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* ── VIEW RESULT MODAL ── */}
      <Dialog open={isViewModalOpen} onOpenChange={setIsViewModalOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl">
              <GraduationCap className="h-6 w-6 text-primary" />
              Evaluation Report: {selectedEval?.studentName}
            </DialogTitle>
            <DialogDescription>
              Stored assessment record generated on {selectedEval && new Date(selectedEval.created_at).toLocaleString()}
            </DialogDescription>
          </DialogHeader>

          {isLoadingEval ? (
            <div className="py-20 flex flex-col items-center justify-center gap-4">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              <p className="text-muted-foreground animate-pulse">Retrieving and Hydrating Evaluation Data...</p>
            </div>
          ) : selectedEval ? (
            <div className="space-y-6 py-4">
              {/* Score Summary */}
              <div className="grid grid-cols-3 gap-4">
                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-6 text-center">
                    <p className="text-sm text-muted-foreground uppercase font-semibold">Marks Obtained</p>
                    <p className="text-4xl font-bold text-primary">{selectedEval.total_marks}/{selectedEval.max_marks}</p>
                  </CardContent>
                </Card>
                <Card className="bg-primary/5 border-primary/20">
                  <CardContent className="pt-6 text-center">
                    <p className="text-sm text-muted-foreground uppercase font-semibold">Percentage</p>
                    <p className="text-4xl font-bold text-primary">{selectedEval.percentage}%</p>
                  </CardContent>
                </Card>
                <Card className={`${selectedEval.result === 'PASS' ? 'bg-green-500/10 border-green-500/20' : 'bg-destructive/10 border-destructive/20'}`}>
                  <CardContent className="pt-6 text-center">
                    <p className="text-sm text-muted-foreground uppercase font-semibold">Result</p>
                    <p className={`text-4xl font-bold ${selectedEval.result === 'PASS' ? 'text-green-600' : 'text-destructive'}`}>
                      {selectedEval.result}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Question Breakdown */}
              <div className="space-y-3">
                <h3 className="font-bold text-lg flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" /> Question-wise Breakdown
                </h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-muted">
                      <tr>
                        <th className="px-4 py-2 text-left">Q.No</th>
                        <th className="px-4 py-2 text-left">Marks</th>
                        <th className="px-4 py-2 text-left">Feedback Insight</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {Object.entries(selectedEval.question_details).map(([qNum, details]: [string, any]) => (
                        <tr key={qNum} className="hover:bg-muted/30">
                          <td className="px-4 py-3 font-medium">Question {qNum}</td>
                          <td className="px-4 py-3">
                            <Badge variant="secondary">{details.marks_obtained}/{details.max_marks}</Badge>
                          </td>
                          <td className="px-4 py-3 text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed">
                            {details.examiner_note}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Overall Feedback */}
              <div className="p-4 rounded-lg bg-muted border space-y-2">
                <h3 className="font-bold flex items-center gap-2">
                  <FileText className="h-4 w-4" /> Evaluator Summary Note
                </h3>
                <p className="text-sm whitespace-pre-wrap leading-relaxed text-muted-foreground">
                  {selectedEval.feedback}
                </p>
              </div>
              
              <div className="pt-4 border-t text-[10px] text-muted-foreground text-center">
                This is a read-only snapshot. To re-run the AI pipeline, use the 'Re-Evaluate' function in the dashboard.
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-muted-foreground">
              Failed to load evaluation record.
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ClassDetail;
