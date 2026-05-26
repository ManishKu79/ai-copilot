import os
from typing import Dict, List, Any
from datetime import datetime


class DocumentationGenerator:
    def __init__(self):
        self.sections_order = [
            "title",
            "badges",
            "description",
            "features",
            "tech_stack",
            "installation",
            "usage",
            "api_reference",
            "project_structure",
            "configuration",
            "testing",
            "contributing",
            "license",
        ]

    def generate_readme(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate complete README.md"""

        readme_sections = []

        # Title
        repo_name = repo_analysis.get("name", "Project")
        readme_sections.append(f"# 🚀 {repo_name}\n")

        # Badges
        readme_sections.append(self._generate_badges(repo_analysis))

        # Description
        readme_sections.append(self._generate_description(repo_analysis))

        # Features
        readme_sections.append(self._generate_features(repo_analysis))

        # Tech Stack
        readme_sections.append(self._generate_tech_stack(repo_analysis))

        # Installation
        readme_sections.append(self._generate_installation(repo_analysis))

        # Usage
        readme_sections.append(self._generate_usage(repo_analysis))

        # API Reference
        if self._has_api_endpoints(repo_analysis):
            readme_sections.append(
                self._generate_api_reference(repo_analysis)
            )

        # Project Structure
        readme_sections.append(
            self._generate_project_structure(repo_analysis)
        )

        # Configuration
        readme_sections.append(
            self._generate_configuration(repo_analysis)
        )

        # Testing
        readme_sections.append(
            self._generate_testing_section(repo_analysis)
        )

        # Contributing
        readme_sections.append(self._generate_contributing())

        # License
        readme_sections.append(
            self._generate_license(repo_analysis)
        )

        # Footer
        readme_sections.append(self._generate_footer())

        return "\n\n".join(readme_sections)

    def _generate_badges(self, analysis: Dict[str, Any]) -> str:
        """Generate README badges"""

        coverage = analysis.get("test_coverage", 75)
        complexity = analysis.get("complexity_score", 5)

        coverage_color = (
            "brightgreen"
            if coverage >= 80
            else "yellow"
            if coverage >= 60
            else "red"
        )

        complexity_color = (
            "brightgreen"
            if complexity <= 3
            else "yellow"
            if complexity <= 6
            else "orange"
        )

        badges = [
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)",
            "![License](https://img.shields.io/badge/license-MIT-green)",
            "![Build](https://img.shields.io/badge/build-passing-brightgreen)",
            f"![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-{coverage_color})",
            f"![Complexity](https://img.shields.io/badge/complexity-{complexity}/10-{complexity_color})",
        ]

        return "\n".join(badges)

    def _generate_description(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate project description"""

        repo_name = analysis.get("name", "Project")
        files_count = analysis.get("files_count", 0)
        total_lines = analysis.get("total_lines", 0)
        complexity = analysis.get("complexity_score", "N/A")

        languages = analysis.get("languages", {})

        if languages:
            main_lang = max(
                languages.items(),
                key=lambda x: x[1]
            )[0]
        else:
            main_lang = "multiple"

        return f"""## 📖 Description

**{repo_name}** is a modern {main_lang}-based project designed with scalability, maintainability, and performance in mind.

### 📊 Project Metrics

- **Total Files:** {files_count}
- **Lines of Code:** {total_lines}
- **Complexity Score:** {complexity}/10
- **Primary Language:** {main_lang.capitalize()}

This project follows modern software engineering practices and clean architecture principles.
"""

    def _generate_features(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate features section"""

        files = analysis.get("files_preview", [])
        file_names = [
            file.get("name", "").lower()
            for file in files
        ]

        features = set()

        feature_map = {
            "api": "🌐 REST API support",
            "auth": "🔐 Authentication system",
            "database": "💾 Database integration",
            "docker": "🐳 Docker support",
            "test": "🧪 Automated testing",
            "cli": "💻 Command-line interface",
            "web": "🎨 Responsive frontend",
            "ai": "🤖 AI-powered functionality",
        }

        for name in file_names:
            for key, feature in feature_map.items():
                if key in name:
                    features.add(feature)

        if not features:
            features = {
                "⚡ High-performance architecture",
                "📦 Modular project structure",
                "🛠️ Easy customization",
            }

        result = ["## ✨ Features\n"]

        for feature in sorted(features):
            result.append(f"- {feature}")

        return "\n".join(result)

    def _generate_tech_stack(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate tech stack section"""

        languages = analysis.get("languages", {})
        technologies = analysis.get("technologies", [])

        result = ["## 🛠️ Tech Stack\n"]

        if languages:
            result.append("### Languages\n")

            for lang, count in languages.items():
                result.append(
                    f"- **{lang.capitalize()}** ({count} files)"
                )

            result.append("")

        if technologies:
            result.append("### Frameworks & Libraries\n")

            for tech in technologies[:10]:
                result.append(f"- {tech}")

        return "\n".join(result)

    def _generate_installation(
        self,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate installation section"""

        files = analysis.get("files_preview", [])

        has_package_json = any(
            file.get("name") == "package.json"
            for file in files
        )

        has_requirements = any(
            file.get("name") == "requirements.txt"
            for file in files
        )

        repo_name = analysis.get("name", "project")

        installation = f"""## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/username/{repo_name}.git
cd {repo_name}