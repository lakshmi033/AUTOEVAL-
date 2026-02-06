import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/hooks/use-theme";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import Login from "./pages/Login";
import StudentLogin from "./pages/StudentLogin";
import TeacherLogin from "./pages/TeacherLogin";
import Register from "./pages/Register";
import StudentDashboard from "./pages/StudentDashboard";
import TeacherDashboard from "./pages/TeacherDashboard";
import ClassDetail from "./pages/ClassDetail";
import TeacherEvaluation from "./pages/TeacherEvaluation";
import EvaluationResult from "./pages/EvaluationResult";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/student-login" element={<StudentLogin />} />
              <Route path="/teacher-login" element={<TeacherLogin />} />
              <Route path="/register" element={<Register />} />
              <Route 
                path="/student-dashboard" 
                element={
                  <ProtectedRoute allowedRole="student">
                    <StudentDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/teacher-dashboard" 
                element={
                  <ProtectedRoute allowedRole="teacher">
                    <TeacherDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/teacher/class/:classId" 
                element={
                  <ProtectedRoute allowedRole="teacher">
                    <ClassDetail />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/teacher/class/:classId/evaluate/:studentId" 
                element={
                  <ProtectedRoute allowedRole="teacher">
                    <TeacherEvaluation />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/teacher/class/:classId/result/:studentId" 
                element={
                  <ProtectedRoute allowedRole="teacher">
                    <EvaluationResult />
                  </ProtectedRoute>
                } 
              />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </TooltipProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
