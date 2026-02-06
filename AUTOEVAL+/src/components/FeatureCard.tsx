import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  delay?: number;
}

export const FeatureCard = ({ icon: Icon, title, description, delay = 0 }: FeatureCardProps) => {
  return (
    <div 
      className="group relative bg-card border border-border rounded-lg p-8 shadow-soft hover:shadow-soft-lg transition-base animate-fade-in-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-base" />
      
      <div className="relative">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-lg bg-primary-light mb-6 group-hover:scale-110 transition-base">
          <Icon className="h-7 w-7 text-primary" />
        </div>
        
        <h3 className="text-xl font-semibold mb-3 text-card-foreground">
          {title}
        </h3>
        
        <p className="text-muted-foreground leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
};
