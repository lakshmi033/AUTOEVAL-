import { api } from '@/lib/api';

export interface Student {
    id: string | number;
    name: string;
    rollNumber: string;
    evaluated: boolean;
    marks?: number;
    grade?: string;
    email?: string;
}

export interface Classroom {
    id: number;
    name: string;
    teacher_id: number;
    created_at: string;
}

export interface ClassroomWithStats extends Classroom {
    studentCount: number;
    evaluatedCount: number;
}

export const ClassroomService = {
    // Fetch all classrooms for the teacher
    getClassrooms: async (): Promise<Classroom[]> => {
        try {
            const response = await api.get('/classrooms');
            return response.data;
        } catch (error) {
            console.error("Error fetching classrooms:", error);
            throw error;
        }
    },

    // Fetch classrooms with student counts (Frontend aggregation)
    getClassroomsWithStats: async (): Promise<ClassroomWithStats[]> => {
        try {
            const classrooms = await ClassroomService.getClassrooms();

            // Fetch student counts for each class in parallel
            const statsPromises = classrooms.map(async (c) => {
                try {
                    const students = await ClassroomService.getStudents(String(c.id));
                    const evaluated = students.filter(s => s.evaluated).length;
                    return {
                        ...c,
                        studentCount: students.length,
                        evaluatedCount: evaluated
                    };
                } catch (e) {
                    return { ...c, studentCount: 0, evaluatedCount: 0 };
                }
            });

            return await Promise.all(statsPromises);
        } catch (error) {
            console.error("Error fetching classroom stats:", error);
            throw error;
        }
    },

    // Create a new classroom
    createClassroom: async (name: string): Promise<Classroom> => {
        try {
            const response = await api.post('/classrooms', { name });
            return response.data;
        } catch (error) {
            console.error("Error creating classroom:", error);
            throw error;
        }
    },

    // Get students in a specific classroom
    getStudents: async (classroomId: string): Promise<Student[]> => {
        try {
            const response = await api.get(`/classrooms/${classroomId}/students`);
            // Map backend response (StudentProfileRead) to frontend Student interface
            return response.data.map((s: any) => ({
                id: s.id,
                name: s.full_name || s.email, // Fallback to email if name is missing
                rollNumber: s.role_number || `S-${s.id}`, // Fallback ID-based roll number
                evaluated: false,
                email: s.email
            }));
        } catch (error) {
            console.error(`Error fetching students for class ${classroomId}:`, error);
            throw error;
        }
    },

    // Add a student to a classroom
    addStudent: async (classroomId: string, name: string, rollNumber: string, email?: string): Promise<Student> => {
        try {
            const payload = {
                roll_number: rollNumber,
                full_name: name,
                email: email || `${rollNumber.toLowerCase()}@school.com` // Auto-generate email if missing
            };

            const response = await api.post(`/classrooms/${classroomId}/students/add`, payload);
            const s = response.data;

            return {
                id: s.id,
                name: s.full_name,
                rollNumber: s.roll_number,
                evaluated: false,
                email: s.email
            };
        } catch (error) {
            console.error("Error adding student:", error);
            throw error;
        }
    }
};
