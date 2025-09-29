import React from 'react';
import { 
  HeartIcon,
  CodeBracketIcon,
  ShieldCheckIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-neutral-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-neutral-600">
          <div className="flex items-center gap-2">
            <CpuChipIcon className="w-4 h-4" />
            <span>Independent ERP System</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1">
            <ShieldCheckIcon className="w-4 h-4" />
            <span>Secure & Reliable</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1">
            <CodeBracketIcon className="w-4 h-4" />
            <span>Open Source</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-neutral-600">
          <span>© {currentYear} All rights reserved</span>
          <div className="flex items-center gap-1">
            <span>Made with</span>
            <HeartIcon className="w-4 h-4 text-red-500" />
            <span>by Ahmed Ashour</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
