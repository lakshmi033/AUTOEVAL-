import { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent } from '@/components/ui/card';
import { BookOpen } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { ClassroomService, ClassroomWithStats } from '@/services/ClassroomService';
import { toast } from '@/hooks/use-toast';

const TeacherDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleClassClick = (classId: number) => {
    navigate(`/teacher/class/${classId}`);
  };

  const [classes, setClasses] = useState<ClassroomWithStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const data = await ClassroomService.getClassroomsWithStats();
        setClasses(data);
      } catch (error) {
        toast({ title: "Error", description: "Failed to load classrooms", variant: "destructive" });
      } finally {
        setLoading(false);
      }
    };
    fetchClasses();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          {/* Welcome Section */}
          <div className="mb-12 animate-fade-in text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light mb-4">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome, {user?.username || 'Teacher'}!
            </h1>
            {user?.department && (
              <p className="text-muted-foreground">Department: {user.department}</p>
            )}
            <p className="text-lg text-muted-foreground mt-4">
              Select a class to manage students and evaluate answer sheets
            </p>
          </div>

          {/* Class Cards */}
          {loading ? (
            <div className="text-center py-10">Loading classrooms...</div>
          ) : classes.length === 0 ? (
            <div className="text-center py-10 border-2 border-dashed rounded-xl">
              <p className="text-muted-foreground">No classrooms found. Create one to get started.</p>
              {/* Potential Add Class Button here later */}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {classes.map((classItem, index) => {
                return (
                  <Card
                    key={classItem.id}
                    onClick={() => handleClassClick(classItem.id)}
                    className="shadow-soft animate-fade-in-up cursor-pointer hover:shadow-soft-lg hover:scale-105 transition-all duration-300 border-2 hover:border-primary"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardContent className="pt-8 pb-8 text-center">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary-light mb-6">
                        <BookOpen className="h-10 w-10 text-primary" />
                      </div>
                      <h2 className="text-2xl font-bold mb-4">{classItem.name}</h2>
                      <div className="space-y-2 text-sm text-muted-foreground">
                        <p>Students: {classItem.studentCount}</p>
                        <p>Evaluated: {classItem.evaluatedCount}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Instructions */}
          <div className="mt-12 text-center animate-fade-in" style={{ animationDelay: '400ms' }}>
            <p className="text-muted-foreground">
              Click on a class to view students, add new students, and evaluate answer sheets
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TeacherDashboard;
