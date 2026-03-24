import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import {
  GraduationCap,
  BookOpen,
  MessageSquare,
  BarChart3,
  LogOut,
  ChevronRight,
  X,
  Award,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';

// ─── Types ──────────────────────────────────────────────
interface StudentMeta {
  fullName: string;
  rollNumber: string | number;
  className: string;
  isEvaluated: boolean;
}

interface SubjectMarks {
  subject: string;
  total_marks: number;
  total_max_marks: number;
  percentage: number;
  question_details: Record<string, any>;
  evaluated_at?: string;
}

// ─── Constants ──────────────────────────────────────────
const SUBJECTS = ['Civics', 'History', 'Geography'];
const INTERNAL_COLOR: Record<string, string> = {
  Civics: 'from-violet-500 to-purple-600',
  History: 'from-amber-500 to-orange-600',
  Geography: 'from-emerald-500 to-teal-600',
};

// ─── Main Component ─────────────────────────────────────
const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Persist student metadata from localStorage after login
  const [meta, setMeta] = useState<StudentMeta>(() => {
    try {
      const stored = localStorage.getItem('student_meta');
      return stored ? JSON.parse(stored) : { fullName: '', rollNumber: '', className: '', isEvaluated: false };
    } catch {
      return { fullName: '', rollNumber: '', className: '', isEvaluated: false };
    }
  });

  const [selectedInternal, setSelectedInternal] = useState<1 | 2>(1);
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [marks, setMarks] = useState<SubjectMarks | null>(null);
  const [marksLoading, setMarksLoading] = useState(false);
  const [marksError, setMarksError] = useState<string | null>(null);

  // Modal state
  const [showMarksModal, setShowMarksModal] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedback, setFeedback] = useState<string>('');
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  // Populate from user context if meta is empty
  useEffect(() => {
    if (user && !meta.fullName) {
      setMeta({
        fullName: user.username || 'Student',
        rollNumber: (user as any).rollNumber || '',
        className: (user as any).className || '',
        isEvaluated: false,
      });
    }
  }, [user]);

  const handleSubjectClick = async (subject: string) => {
    setSelectedSubject(subject);
    setMarks(null);
    setMarksError(null);
    setMarksLoading(true);
    try {
      const res = await api.get(`/student/marks/${encodeURIComponent(subject)}`);
      setMarks(res.data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'No evaluation found for this subject.';
      setMarksError(detail);
    } finally {
      setMarksLoading(false);
    }
  };

  const handleViewFeedback = async () => {
    if (!selectedSubject) return;
    setFeedback('');
    setFeedbackLoading(true);
    setShowFeedbackModal(true);
    try {
      const res = await api.get(`/student/feedback/${encodeURIComponent(selectedSubject)}`);
      setFeedback(res.data.feedback || 'No feedback available.');
    } catch (err: any) {
      setFeedback(err?.response?.data?.detail || 'No feedback found for this subject.');
    } finally {
      setFeedbackLoading(false);
    }
  };

  const passFail = marks ? (marks.percentage >= 40 ? 'PASSED' : 'FAILED') : null;

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      
      {/* ── LEFT SIDEBAR ─────────────────────────────── */}
      <aside className="w-72 min-h-screen bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 flex flex-col shadow-lg">
        
        {/* Logo */}
        <div className="px-6 py-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-xs font-semibold text-primary uppercase tracking-widest">AutoEval+</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Student Portal</p>
            </div>
          </div>
        </div>

        {/* Student Identity Card */}
        <div className="px-6 py-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center flex-shrink-0 shadow-inner">
              <span className="text-2xl font-bold text-primary">
                {(meta.fullName || user?.username || 'S')[0].toUpperCase()}
              </span>
            </div>
            <div className="min-w-0">
              <h2 className="font-bold text-slate-900 dark:text-white text-lg leading-snug truncate">
                {meta.fullName || user?.username || 'Student'}
              </h2>
              <div className="mt-1.5 space-y-0.5">
                <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary inline-block"></span>
                  Roll No: <strong className="text-slate-700 dark:text-slate-300">{meta.rollNumber || '—'}</strong>
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary inline-block"></span>
                  Class: <strong className="text-slate-700 dark:text-slate-300">{meta.className || '—'}</strong>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation: Internals */}
        <nav className="flex-1 px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500 px-2 mb-2">
            Examinations
          </p>
          {[1, 2].map((num) => (
            <button
              key={num}
              onClick={() => { setSelectedInternal(num as 1 | 2); setSelectedSubject(null); setMarks(null); setMarksError(null); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl mb-1 transition-all text-base font-medium ${
                selectedInternal === num
                  ? 'bg-primary text-white shadow-md shadow-primary/30'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <BookOpen className="h-4 w-4 flex-shrink-0" />
              Internals {num}
              <ChevronRight className={`h-3 w-3 ml-auto transition-transform ${selectedInternal === num ? 'rotate-90 opacity-0' : ''}`} />
            </button>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-4 pb-6">
          <button
            onClick={() => { localStorage.removeItem('student_meta'); logout(); }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-base font-medium text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── MAIN CONTENT ─────────────────────────────── */}
      <main className="flex-1 p-8 overflow-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Internals {selectedInternal}
          </h1>
          <p className="text-base text-slate-500 dark:text-slate-400 mt-1">
            {selectedInternal === 1 ? 'Select a subject to view your evaluation results.' : 'No evaluation has been conducted for Internals 2 yet.'}
          </p>
        </div>

        {/* Internals 2 — empty state */}
        {selectedInternal === 2 && (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="w-20 h-20 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 shadow-inner">
              <Clock className="h-10 w-10 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-slate-600 dark:text-slate-300">No evaluation conducted yet</h3>
            <p className="text-base text-slate-400 mt-2 max-w-sm">
              Your teacher has not run the Internals 2 evaluation. Check back later.
            </p>
          </div>
        )}

        {/* Internals 1 — Subject Cards */}
        {selectedInternal === 1 && (
          <div className="grid lg:grid-cols-3 gap-6">
            
            {/* Left: Subject List */}
            <div className="lg:col-span-1 space-y-3">
              {SUBJECTS.map((subject) => (
                <button
                  key={subject}
                  onClick={() => handleSubjectClick(subject)}
                  className={`w-full group relative overflow-hidden rounded-2xl p-5 text-left transition-all duration-300 shadow-sm hover:shadow-lg ${
                    selectedSubject === subject
                      ? 'ring-2 ring-primary shadow-primary/20'
                      : 'bg-white dark:bg-slate-900 hover:scale-[1.02]'
                  }`}
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${INTERNAL_COLOR[subject]} opacity-${selectedSubject === subject ? '100' : '0 group-hover:opacity-100'} transition-opacity duration-300`} />
                  <div className="relative">
                    <div className={`w-9 h-9 rounded-xl mb-3 flex items-center justify-center ${
                      selectedSubject === subject ? 'bg-white/20' : 'bg-slate-100 dark:bg-slate-800 group-hover:bg-white/20'
                    } transition-colors`}>
                      <BookOpen className={`h-4 w-4 ${selectedSubject === subject ? 'text-white' : 'text-primary group-hover:text-white'}`} />
                    </div>
                    <p className={`font-semibold text-base ${selectedSubject === subject ? 'text-white' : 'text-slate-900 dark:text-white group-hover:text-white'}`}>
                      {subject}
                    </p>
                    <p className={`text-xs mt-0.5 ${selectedSubject === subject ? 'text-white/80' : 'text-slate-400 group-hover:text-white/80'}`}>
                      Internals 1
                    </p>
                  </div>
                </button>
              ))}
            </div>

            {/* Right: Results Panel */}
            <div className="lg:col-span-2">
              
              {/* No subject selected */}
              {!selectedSubject && (
                <div className="h-full flex flex-col items-center justify-center min-h-[300px] text-center bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-dashed border-slate-200 dark:border-slate-700 p-8">
                  <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
                    <BarChart3 className="h-8 w-8 text-slate-300" />
                  </div>
                  <h3 className="font-semibold text-slate-500 dark:text-slate-400">Select a subject</h3>
                  <p className="text-xs text-slate-400 mt-1">Click on a subject card to view your mark details.</p>
                </div>
              )}

              {/* Loading */}
              {selectedSubject && marksLoading && (
                <div className="h-full flex flex-col items-center justify-center min-h-[300px] bg-white dark:bg-slate-900 rounded-2xl shadow-sm">
                  <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent mb-3" />
                  <p className="text-sm text-slate-400 animate-pulse">Loading results...</p>
                </div>
              )}

              {/* Error / No data */}
              {selectedSubject && !marksLoading && marksError && (
                <div className="h-full flex flex-col items-center justify-center min-h-[300px] bg-white dark:bg-slate-900 rounded-2xl shadow-sm p-8 text-center">
                  <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center mb-4">
                    <AlertCircle className="h-8 w-8 text-amber-500" />
                  </div>
                  <h3 className="font-semibold text-slate-700 dark:text-slate-300">Not yet evaluated</h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs">
                    No evaluation has been recorded for <strong>{selectedSubject}</strong>. Please check with your teacher.
                  </p>
                </div>
              )}

              {/* Marks Data */}
              {selectedSubject && !marksLoading && marks && !marksError && (
                <div className="space-y-4 animate-fade-in">
                  
                  {/* Score Cards */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-sm text-center border border-slate-100 dark:border-slate-800">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Marks</p>
                      <p className="text-3xl font-bold text-slate-900 dark:text-white">
                        {marks.total_marks}
                        <span className="text-base font-normal text-slate-400">/{marks.total_max_marks}</span>
                      </p>
                    </div>
                    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-sm text-center border border-slate-100 dark:border-slate-800">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Percentage</p>
                      <p className="text-3xl font-bold text-primary">{marks.percentage}%</p>
                    </div>
                    <div className={`rounded-2xl p-5 shadow-sm text-center border ${
                      passFail === 'PASSED'
                        ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-700'
                        : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700'
                    }`}>
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Result</p>
                      <div className="flex items-center justify-center gap-1.5">
                        {passFail === 'PASSED'
                          ? <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                          : <XCircle className="h-5 w-5 text-red-500" />}
                        <p className={`text-xl font-bold ${passFail === 'PASSED' ? 'text-emerald-600' : 'text-red-600'}`}>
                          {passFail}
                        </p>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-1">Threshold: 40%</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowMarksModal(true)}
                      className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-white dark:bg-slate-900 hover:bg-primary hover:text-white dark:hover:bg-primary rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300 transition-all duration-200 group"
                    >
                      <BarChart3 className="h-4 w-4 group-hover:scale-110 transition-transform" />
                      View Question-wise Marks
                    </button>
                    <button
                      onClick={handleViewFeedback}
                      className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-white dark:bg-slate-900 hover:bg-primary hover:text-white dark:hover:bg-primary rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300 transition-all duration-200 group"
                    >
                      <MessageSquare className="h-4 w-4 group-hover:scale-110 transition-transform" />
                      View Teacher Feedback
                    </button>
                  </div>

                  {/* Evaluated on */}
                  {marks.evaluated_at && (
                    <p className="text-xs text-slate-400 text-right px-1">
                      Evaluated on: {new Date(marks.evaluated_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* ── QUESTION-WISE MARKS MODAL ─────────────────── */}
      {showMarksModal && marks && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => setShowMarksModal(false)}>
          <div
            className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-primary" />
                <h3 className="font-bold text-slate-900 dark:text-white">Question-wise Marks</h3>
              </div>
              <button onClick={() => setShowMarksModal(false)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <X className="h-4 w-4 text-slate-500" />
              </button>
            </div>
            <div className="overflow-y-auto max-h-[calc(80vh-72px)]">
              {Object.keys(marks.question_details).length === 0 ? (
                <div className="py-12 text-center text-slate-400 text-sm">No question breakdown available.</div>
              ) : (
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-slate-50 dark:bg-slate-800">
                    <tr>
                      <th className="px-5 py-3 text-left text-xs font-semibold uppercase text-slate-500">Question</th>
                      <th className="px-5 py-3 text-center text-xs font-semibold uppercase text-slate-500">Marks</th>
                      <th className="px-5 py-3 text-center text-xs font-semibold uppercase text-slate-500">Max</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {Object.entries(marks.question_details)
                      .sort(([a], [b]) => parseInt(a) - parseInt(b))
                      .map(([qNum, detail]: [string, any]) => (
                        <tr key={qNum} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                          <td className="px-5 py-3 font-medium text-slate-700 dark:text-slate-300">Question {qNum}</td>
                          <td className="px-5 py-3 text-center font-bold text-primary">{detail.marks_obtained}</td>
                          <td className="px-5 py-3 text-center text-slate-400">{detail.max_marks}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── FEEDBACK MODAL ────────────────────────────── */}
      {showFeedbackModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4" onClick={() => setShowFeedbackModal(false)}>
          <div
            className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-lg max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                <h3 className="font-bold text-slate-900 dark:text-white">Teacher Feedback</h3>
                <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">{selectedSubject}</span>
              </div>
              <button onClick={() => setShowFeedbackModal(false)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <X className="h-4 w-4 text-slate-500" />
              </button>
            </div>
            <div className="p-5 overflow-y-auto max-h-[calc(80vh-72px)]">
              {feedbackLoading ? (
                <div className="flex flex-col items-center py-12 gap-3">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  <p className="text-sm text-slate-400 animate-pulse">Loading feedback...</p>
                </div>
              ) : (
                <pre className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                  {feedback}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
