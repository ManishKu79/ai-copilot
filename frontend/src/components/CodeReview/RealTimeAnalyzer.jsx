// frontend/src/components/CodeReview/RealTimeAnalyzer.jsx
import { useEffect, useRef } from 'react';
import * as monaco from 'monaco-editor';

export const useRealTimeAnalysis = (editor, reviewCallback) => {
  const debounceTimer = useRef(null);
  
  useEffect(() => {
    if (!editor) return;
    
    const model = editor.getModel();
    if (!model) return;
    
    const disposables = [];
    
    // Add marker for each issue
    const addMarkers = (issues) => {
      const markers = issues.map(issue => ({
        severity: getMonacoSeverity(issue.severity),
        startLineNumber: issue.line,
        startColumn: issue.column || 1,
        endLineNumber: issue.line,
        endColumn: 1000,
        message: `${issue.message}\n\n💡 ${issue.suggestion}`,
        code: issue.rule_id
      }));
      
      monaco.editor.setModelMarkers(model, 'code-review', markers);
    };
    
    // Real-time analysis on content change
    const handleContentChange = () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
      
      debounceTimer.current = setTimeout(async () => {
        const code = editor.getValue();
        const results = await reviewCallback(code);
        
        if (results && results.issues_by_category) {
          const allIssues = [
            ...results.issues_by_category.critical,
            ...results.issues_by_category.high,
            ...results.issues_by_category.medium,
            ...results.issues_by_category.low
          ];
          addMarkers(allIssues);
        }
      }, 1000);
    };
    
    model.onDidChangeContent(handleContentChange);
    
    return () => {
      if (disposables) {
        disposables.forEach(d => d.dispose());
      }
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [editor, reviewCallback]);
};

const getMonacoSeverity = (severity) => {
  switch(severity) {
    case 'critical': return monaco.MarkerSeverity.Error;
    case 'high': return monaco.MarkerSeverity.Error;
    case 'medium': return monaco.MarkerSeverity.Warning;
    case 'low': return monaco.MarkerSeverity.Info;
    default: return monaco.MarkerSeverity.Info;
  }
};