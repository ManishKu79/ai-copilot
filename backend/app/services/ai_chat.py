from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class AIChatAssistant:
    def __init__(self):
        self.conversations = {}
        self.context_window = 10

    def chat(self, message: str, repository_data: Dict[str, Any], conversation_id: Optional[str] = None) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = "conv_" + str(int(datetime.now().timestamp()))

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "history": [],
                "context": repository_data
            }

        conversation = self.conversations[conversation_id]
        response = self._generate_contextual_response(message, repository_data)

        conversation["history"].append({
            "user": message,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })

        if len(conversation["history"]) > self.context_window:
            conversation["history"] = conversation["history"][-self.context_window:]

        return {
            "success": True,
            "conversation_id": conversation_id,
            "response": response,
            "suggested_questions": self._get_suggested_questions(message, repository_data),
            "timestamp": datetime.now().isoformat()
        }

    def _generate_contextual_response(self, message: str, repo_data: Dict[str, Any]) -> str:
        msg_lower = message.lower()

        file_names = [f.get("name", "") for f in repo_data.get("files_preview", [])]

        if any(word in msg_lower for word in ["architecture", "structure", "overview", "system", "design"]):
            return self._analyze_architecture(repo_data)
        elif any(word in msg_lower for word in ["frontend", "ui", "component", "react", "page"]):
            return self._analyze_frontend(repo_data)
        elif any(word in msg_lower for word in ["backend", "api", "server", "route", "endpoint"]):
            return self._analyze_backend(repo_data)
        elif any(word in msg_lower for word in ["complexity", "complex", "maintainability"]):
            return self._analyze_complexity(repo_data)
        elif any(word in msg_lower for word in ["controller", "handler", "route"]):
            return self._analyze_controllers(repo_data, file_names)
        elif any(word in msg_lower for word in ["error", "bug", "fix", "debug", "issue"]):
            return self._analyze_errors()
        elif any(word in msg_lower for word in ["review", "quality", "improve", "analysis"]):
            return self._analyze_code_quality(repo_data)
        elif any(word in msg_lower for word in ["dependency", "package", "library", "import"]):
            return self._analyze_dependencies(repo_data, file_names)
        else:
            return self._get_help_message(repo_data)

    def _analyze_architecture(self, repo_data: Dict[str, Any]) -> str:
        name = repo_data.get("name", "Unknown Project")
        files_count = repo_data.get("files_count", 0)
        total_lines = repo_data.get("total_lines", 0)
        complexity = repo_data.get("complexity_score", 5)
        languages = repo_data.get("languages", {})
        technologies = repo_data.get("technologies", [])
        files = repo_data.get("files_preview", [])

        lines = []
        lines.append("## Architecture Analysis")
        lines.append("")
        lines.append("### Project: " + name)
        lines.append("")
        lines.append("### Statistics")
        lines.append("- Total Files: " + str(files_count))
        lines.append("- Total Lines: " + str(total_lines))
        lines.append("- Complexity Score: " + str(complexity) + "/10")
        lines.append("")

        if languages:
            lines.append("### Languages")
            for lang, count in list(languages.items())[:5]:
                lines.append("- " + lang + ": " + str(count) + " files")
            lines.append("")

        if technologies:
            lines.append("### Technologies")
            for tech in technologies[:8]:
                lines.append("- " + tech)
            lines.append("")

        lines.append("### Main Directories")
        directories = set()
        for file in files:
            path = file.get("path", "")
            if "/" in path:
                directories.add(path.split("/")[0])

        for directory in sorted(list(directories))[:10]:
            lines.append("- " + directory + "/")

        lines.append("")
        lines.append("### Assessment")
        if complexity <= 4:
            lines.append("Low complexity - Well structured")
        elif complexity <= 7:
            lines.append("Moderate complexity - Monitor closely")
        else:
            lines.append("High complexity - Needs refactoring")

        return "\n".join(lines)

    def _analyze_frontend(self, repo_data: Dict[str, Any]) -> str:
        files = repo_data.get("files_preview", [])
        frontend_files = []

        for file in files:
            name = file.get("name", "").lower()
            if any(ext in name for ext in [".jsx", ".tsx", ".vue", ".css", ".scss", ".html"]):
                frontend_files.append(file.get("name"))

        lines = []
        lines.append("## Frontend Analysis")
        lines.append("")
        lines.append("Frontend files detected: " + str(len(frontend_files)))
        lines.append("")

        if frontend_files:
            lines.append("### Components Found")
            for f in frontend_files[:15]:
                lines.append("- " + f)

        lines.append("")
        lines.append("### Recommendations")
        lines.append("- Use reusable components")
        lines.append("- Implement lazy loading")
        lines.append("- Add loading states")
        lines.append("- Improve error boundaries")

        return "\n".join(lines)

    def _analyze_backend(self, repo_data: Dict[str, Any]) -> str:
        files = repo_data.get("files_preview", [])
        backend_files = []

        for file in files:
            name = file.get("name", "").lower()
            if any(ext in name for ext in [".py", ".js", ".ts", ".go"]):
                if "test" not in name:
                    backend_files.append(file.get("name"))

        lines = []
        lines.append("## Backend Analysis")
        lines.append("")
        lines.append("Backend files detected: " + str(len(backend_files)))
        lines.append("")

        if backend_files:
            lines.append("### Core Files")
            for f in backend_files[:15]:
                lines.append("- " + f)

        lines.append("")
        lines.append("### Recommendations")
        lines.append("- Add centralized error handling")
        lines.append("- Implement request validation")
        lines.append("- Add API documentation")
        lines.append("- Use environment variables for config")

        return "\n".join(lines)

    def _analyze_complexity(self, repo_data: Dict[str, Any]) -> str:
        complexity = repo_data.get("complexity_score", 5)
        files = repo_data.get("files_preview", [])

        lines = []
        lines.append("## Complexity Analysis")
        lines.append("")
        lines.append("Overall Score: " + str(complexity) + "/10")
        lines.append("")

        if complexity <= 4:
            lines.append("Low complexity - Good code quality")
        elif complexity <= 7:
            lines.append("Moderate complexity - Needs monitoring")
        else:
            lines.append("High complexity - Needs refactoring")

        high_complexity = []
        for file in files:
            file_complexity = file.get("complexity", 0)
            if file_complexity > 7:
                high_complexity.append((file.get("name"), file_complexity))

        if high_complexity:
            lines.append("")
            lines.append("### High Complexity Files")
            for name, score in high_complexity[:10]:
                lines.append("- " + name + " (" + str(score) + "/10)")

        lines.append("")
        lines.append("### Refactor Suggestions")
        lines.append("- Break large functions into smaller ones")
        lines.append("- Reduce nested conditions")
        lines.append("- Extract reusable utilities")

        return "\n".join(lines)

    def _analyze_controllers(self, repo_data: Dict[str, Any], file_names: List[str]) -> str:
        controllers = []
        for file in file_names:
            if any(word in file.lower() for word in ["controller", "handler", "route"]):
                controllers.append(file)

        lines = []
        lines.append("## Controllers Analysis")
        lines.append("")
        lines.append("Controllers found: " + str(len(controllers)))
        lines.append("")

        if controllers:
            lines.append("### Controller Files")
            for c in controllers[:15]:
                lines.append("- " + c)

        lines.append("")
        lines.append("### Best Practices")
        lines.append("- Keep controllers thin")
        lines.append("- Move business logic to services")
        lines.append("- Add request validation")
        lines.append("- Standardize API responses")

        return "\n".join(lines)

    def _analyze_errors(self) -> str:
        lines = []
        lines.append("## Error Analysis & Debugging")
        lines.append("")
        lines.append("### Common Issues to Check")
        lines.append("1. Module import errors - Verify file paths")
        lines.append("2. API integration issues - Check endpoints")
        lines.append("3. State management problems - Check useEffect dependencies")
        lines.append("4. Null/undefined access - Add optional chaining")
        lines.append("")
        lines.append("### Debugging Strategy")
        lines.append("")
        lines.append("```python")
        lines.append("import logging")
        lines.append("logging.basicConfig(level=logging.DEBUG)")
        lines.append("")
        lines.append("try:")
        lines.append("    result = function_call()")
        lines.append("except Exception as e:")
        lines.append("    logging.error(f'Error: {e}')")
        lines.append("```")
        lines.append("")
        lines.append("Share your specific error message for targeted help!")

        return "\n".join(lines)

    def _analyze_code_quality(self, repo_data: Dict[str, Any]) -> str:
        files = repo_data.get("files_preview", [])
        complexity = repo_data.get("complexity_score", 5)

        quality_issues = []
        for f in files:
            if f.get("lines", 0) > 300:
                quality_issues.append(f.get("name", "unknown") + " - Large file")
            if f.get("complexity", 0) > 7:
                quality_issues.append(f.get("name", "unknown") + " - High complexity")

        lines = []
        lines.append("## Code Quality Analysis")
        lines.append("")
        lines.append("Quality Score: " + str(100 - (complexity * 5)) + "/100")
        lines.append("Issues Found: " + str(len(quality_issues)))
        lines.append("")

        if quality_issues:
            lines.append("### Issues to Address")
            for issue in quality_issues[:5]:
                lines.append("- " + issue)

        lines.append("")
        lines.append("### Improvement Areas")
        lines.append("- Add type hints / TypeScript")
        lines.append("- Increase test coverage")
        lines.append("- Add error handling")
        lines.append("- Improve documentation")
        lines.append("- Remove unused code")

        return "\n".join(lines)

    def _analyze_dependencies(self, repo_data: Dict[str, Any], file_names: List[str]) -> str:
        has_package_json = "package.json" in file_names
        has_requirements = "requirements.txt" in file_names

        lines = []
        lines.append("## Dependency Analysis")
        lines.append("")

        if has_package_json:
            lines.append("Detected: npm/yarn (Node.js)")
        if has_requirements:
            lines.append("Detected: pip (Python)")

        lines.append("")
        lines.append("### Recommended Commands")
        lines.append("")
        lines.append("# Check outdated packages")
        if has_package_json:
            lines.append("npm outdated")
        if has_requirements:
            lines.append("pip list --outdated")
        lines.append("")
        lines.append("# Security audit")
        if has_package_json:
            lines.append("npm audit")
        if has_requirements:
            lines.append("pip-audit")
        lines.append("")
        lines.append("### Best Practices")
        lines.append("- Keep dependencies updated")
        lines.append("- Remove unused packages")
        lines.append("- Use lock files for consistency")
        lines.append("- Review dependency licenses")

        return "\n".join(lines)

    def _get_help_message(self, repo_data: Dict[str, Any]) -> str:
        name = repo_data.get("name", "your repository")
        files_count = repo_data.get("files_count", 0)

        lines = []
        lines.append("## AI Code Assistant")
        lines.append("")
        lines.append("I've analyzed **" + name + "** with " + str(files_count) + " files.")
        lines.append("")
        lines.append("### What I can help with:")
        lines.append("")
        lines.append("| Topic | Example Question |")
        lines.append("|-------|------------------|")
        lines.append("| Architecture | 'Explain the architecture' |")
        lines.append("| Frontend | 'Analyze frontend structure' |")
        lines.append("| Backend | 'Show me backend modules' |")
        lines.append("| Complexity | 'Find complex files' |")
        lines.append("| Controllers | 'About my controllers' |")
        lines.append("| Code Quality | 'Review code quality' |")
        lines.append("| Dependencies | 'List dependencies' |")
        lines.append("| Errors | 'Help debug errors' |")
        lines.append("")
        lines.append("### Try asking:")
        lines.append("1. 'Explain the architecture'")
        lines.append("2. 'Find complexity issues'")
        lines.append("3. 'Review code quality'")
        lines.append("4. 'Analyze frontend'")
        lines.append("5. 'About my controllers'")

        return "\n".join(lines)

    def _get_suggested_questions(self, message: str, repo_data: Dict[str, Any]) -> List[str]:
        msg_lower = message.lower()

        if "architecture" in msg_lower:
            return ["Analyze frontend", "Show backend modules", "Find complexity issues"]
        elif "frontend" in msg_lower:
            return ["List all components", "Suggest frontend improvements", "Review UI structure"]
        elif "complexity" in msg_lower:
            return ["Show complex files", "How to reduce complexity", "Refactor suggestions"]
        else:
            return ["Explain architecture", "Find complexity issues", "Review code quality", "Analyze frontend", "About controllers"]

    def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        if conversation_id in self.conversations:
            return {
                'success': True,
                'history': self.conversations[conversation_id]['history']
            }
        return {'success': False, 'error': 'Conversation not found'}