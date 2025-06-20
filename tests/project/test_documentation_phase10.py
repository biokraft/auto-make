"""
Tests for Phase 10: Documentation Overhaul
Ensures all documentation accurately reflects the agent-first architecture.
"""

import re
from pathlib import Path

import pytest


class TestReadmeDocumentation:
    """Test that README.md accurately reflects the agent-first architecture."""

    @pytest.fixture
    def readme_content(self):
        """Load the README.md content."""
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        return readme_path.read_text()

    def test_readme_emphasizes_multi_agent_system(self, readme_content):
        """Test that README emphasizes the multi-agent system in project description."""
        # Should mention multi-agent system prominently
        assert "multi-agent system" in readme_content.lower()
        assert "manager agent" in readme_content.lower()
        assert (
            "specialist" in readme_content.lower()
            or "specialists" in readme_content.lower()
        )

    def test_readme_describes_manager_agent_workflow(self, readme_content):
        """Test that README describes how the Manager Agent workflow works."""
        # Should explain the manager agent orchestration
        assert "manager agent" in readme_content.lower()
        assert (
            "orchestrat" in readme_content.lower()
        )  # orchestrate/orchestrates/orchestration
        assert (
            "delegate" in readme_content.lower() or "delegat" in readme_content.lower()
        )

    def test_readme_lists_agent_capabilities(self, readme_content):
        """Test that README lists the key agent capabilities."""
        content_lower = readme_content.lower()

        # Should mention key specialist agents
        expected_agents = [
            "terminal",
            "coding",
            "web",
            "makefile",
            "filesystem" or "file system",
        ]

        # At least 3 of the key agents should be mentioned
        mentioned_count = sum(1 for agent in expected_agents if agent in content_lower)
        assert mentioned_count >= 3, (
            f"Only {mentioned_count} agent types mentioned in README"
        )

    def test_readme_has_comprehensive_usage_examples(self, readme_content):
        """Test that README includes comprehensive agent usage examples."""
        # Should have examples of both interactive and non-interactive usage
        assert "automake agent" in readme_content
        assert "automake run" in readme_content or 'automake "' in readme_content

        # Should show different types of commands
        example_patterns = [
            r'automake\s+(run\s+)?"[^"]*"',  # Non-interactive commands
            r"automake\s+agent",  # Interactive mode
        ]

        found_examples = 0
        for pattern in example_patterns:
            if re.search(pattern, readme_content, re.IGNORECASE):
                found_examples += 1

        assert found_examples >= 2, "README should have examples of both usage modes"

    def test_readme_has_agent_focused_features(self, readme_content):
        """Test that README feature list highlights agent capabilities."""
        content_lower = readme_content.lower()

        # Should mention key agent features
        agent_features = [
            "interactive",
            "natural language",
            "ai-native" or "ai native",
            "smolagents",
            "autonomous" or "autonomy",
        ]

        mentioned_features = sum(
            1 for feature in agent_features if feature in content_lower
        )
        assert mentioned_features >= 3, (
            f"Only {mentioned_features} agent features mentioned"
        )

    def test_readme_has_troubleshooting_section(self, readme_content):
        """Test that README includes troubleshooting guidance for agents."""
        content_lower = readme_content.lower()

        # Should have some troubleshooting guidance
        troubleshooting_indicators = [
            "troubleshoot",
            "common issues",
            "problems",
            "error",
            "debug",
        ]

        has_troubleshooting = any(
            indicator in content_lower for indicator in troubleshooting_indicators
        )
        assert has_troubleshooting, "README should include troubleshooting guidance"

    def test_readme_mentions_security_considerations(self, readme_content):
        """Test that README mentions security aspects of agent execution."""
        content_lower = readme_content.lower()

        # Should mention security aspects
        security_terms = ["security", "sandbox", "isolation", "safe"]

        has_security_mention = any(term in content_lower for term in security_terms)
        assert has_security_mention, "README should mention security considerations"


class TestUserGuideExists:
    """Test that a comprehensive user guide exists."""

    def test_user_guide_file_exists(self):
        """Test that USER_GUIDE.md exists in docs directory."""
        user_guide_path = Path(__file__).parent.parent.parent / "docs" / "USER_GUIDE.md"
        assert user_guide_path.exists(), "USER_GUIDE.md should exist in docs directory"

    def test_user_guide_has_agent_content(self):
        """Test that user guide contains agent-specific content."""
        user_guide_path = Path(__file__).parent.parent.parent / "docs" / "USER_GUIDE.md"
        if user_guide_path.exists():
            content = user_guide_path.read_text().lower()

            # Should cover key agent topics
            agent_topics = [
                "multi-agent",
                "interactive",
                "non-interactive",
                "manager agent",
                "specialist",
            ]

            covered_topics = sum(1 for topic in agent_topics if topic in content)
            assert covered_topics >= 3, (
                f"User guide should cover agent topics, found {covered_topics}"
            )


class TestArchitectureDocumentation:
    """Test that architecture documentation exists and is comprehensive."""

    def test_architecture_doc_exists(self):
        """Test that ARCHITECTURE.md exists in docs directory."""
        arch_doc_path = Path(__file__).parent.parent.parent / "docs" / "ARCHITECTURE.md"
        assert arch_doc_path.exists(), "ARCHITECTURE.md should exist in docs directory"

    def test_architecture_doc_covers_multi_agent_system(self):
        """Test that architecture doc covers the multi-agent system."""
        arch_doc_path = Path(__file__).parent.parent.parent / "docs" / "ARCHITECTURE.md"
        if arch_doc_path.exists():
            content = arch_doc_path.read_text().lower()

            # Should cover architecture topics
            arch_topics = [
                "multi-agent",
                "manager agent",
                "specialist",
                "smolagents",
                "data flow",
            ]

            covered_topics = sum(1 for topic in arch_topics if topic in content)
            assert covered_topics >= 4, (
                f"Architecture doc should cover key topics, found {covered_topics}"
            )


class TestProjectMetadata:
    """Test that project metadata reflects agent-first nature."""

    def test_pyproject_toml_description_mentions_agents(self):
        """Test that pyproject.toml description mentions agents."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_path.read_text().lower()

        # Should mention agents in description
        agent_terms = ["agent", "multi-agent", "ai assistant"]
        has_agent_mention = any(term in content for term in agent_terms)
        assert has_agent_mention, "pyproject.toml should mention agents in description"


class TestSpecificationUpdates:
    """Test that key specifications are updated to reflect implementation."""

    @pytest.mark.parametrize(
        "spec_file",
        [
            "specs/01-core-functionality.md",
            "specs/02-cli-and-ux.md",
            "specs/12-autonomous-agent-mode.md",
            "specs/14-agent-interaction-scaffolding.md",
        ],
    )
    def test_core_specs_are_implementation_focused(self, spec_file):
        """Test that core specifications reflect actual implementation."""
        spec_path = Path(__file__).parent.parent.parent / spec_file
        assert spec_path.exists(), f"{spec_file} should exist"

        content = spec_path.read_text().lower()

        # Should reference actual implementation concepts
        implementation_terms = [
            "smolagents",
            "manager agent",
            "specialist",
            "implemented" or "implementation",
        ]

        found_terms = sum(1 for term in implementation_terms if term in content)
        assert found_terms >= 2, f"{spec_file} should reference implementation concepts"
