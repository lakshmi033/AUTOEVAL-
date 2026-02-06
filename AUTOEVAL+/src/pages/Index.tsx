import { Navbar } from '@/components/Navbar';
import { FeatureCard } from '@/components/FeatureCard';
import { Button } from '@/components/ui/button';
import { Upload, ScanText, GitCompare, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-primary-hover bg-clip-text text-transparent">
              Automatic Subjective Answer Evaluation
            </h1>
            <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
              Streamline your grading process with AI-powered OCR technology. Upload answer sheets,
              extract text automatically, and compare with answer keys in seconds.
            </p>
            <div className="flex gap-4 justify-center">
              <Button
                size="lg"
                className="group"
                onClick={() => navigate(isAuthenticated ? (user?.role === 'teacher' ? '/teacher-dashboard' : '/student-dashboard') : '/register')}
              >
                {isAuthenticated ? 'Go to Dashboard' : 'Get Started Free'}
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/login')}>
                Login
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Powerful Features for Modern Evaluation
            </h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to evaluate subjective answers efficiently
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={Upload}
              title="Answer Sheet Upload"
              description="Easily upload handwritten or typed answer sheets in various formats. Support for images and PDF documents."
              delay={0}
            />
            <FeatureCard
              icon={ScanText}
              title="OCR Text Extraction"
              description="Advanced OCR technology extracts text from answer sheets with high accuracy, handling various handwriting styles."
              delay={100}
            />
            <FeatureCard
              icon={GitCompare}
              title="Answer Key Comparison"
              description="Automatically compare extracted answers with your answer key and generate detailed evaluation reports."
              delay={200}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-12 border border-primary/20 animate-scale-in">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Transform Your Grading Process?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join educators who are saving hours of manual grading work
            </p>
            <Button
              size="lg"
              onClick={() => navigate(isAuthenticated ? (user?.role === 'teacher' ? '/teacher-dashboard' : '/student-dashboard') : '/login')}
            >
              {isAuthenticated ? 'Start Evaluating' : 'Create Free Account'}
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
