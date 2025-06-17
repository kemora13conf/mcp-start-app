"""
Advanced search tools for MCP.
"""

import os
import re
import fnmatch
from pathlib import Path
from typing import Optional, List

from mcp.server.fastmcp import FastMCP

# Assuming these imports are available in your project structure
from ..core.constants import DEFAULT_EXCLUDE_PATTERNS, FILE_TYPE_GROUPS
from ..core.utils import should_exclude_file, is_text_file
from ..models.file_models import SearchMatch


# --- Implementation of the search logic ---

def _search_in_files_impl(search_pattern: str, directory: str = ".", file_pattern: str = "*", use_regex: bool = False) -> str:
    """Implementation for searching text patterns across multiple files"""
    try:
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            return f"Directory '{directory}' does not exist"
        
        matches = []
        
        for file_path in path.rglob(file_pattern):
            if file_path.is_file() and is_text_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if use_regex:
                        # Find all lines that contain a match, not just the matches themselves
                        if re.search(search_pattern, content, re.MULTILINE):
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(search_pattern, line):
                                    matches.append(f"{file_path}:{i}: {line.strip()}")
                    else:
                        if search_pattern in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if search_pattern in line:
                                    matches.append(f"{file_path}:{i}: {line.strip()}")
                except Exception:
                    # Ignore files that can't be read
                    continue
        
        if not matches:
            return f"No matches found for '{search_pattern}' in {directory}"
        
        # Limit to 50 results to avoid overwhelming output
        result_limit = 50
        result = f"Found {len(matches)} matches for '{search_pattern}':\n\n"
        result += "\n".join(matches[:result_limit])
        
        if len(matches) > result_limit:
            result += f"\n\n... and {len(matches) - result_limit} more matches"
        
        return result
        
    except Exception as e:
        return f"Error searching files: {str(e)}"


def _search_adv_impl(
    search_term: str,
    search_path: str = ".",
    case_sensitive: bool = False,
    whole_word: bool = False,
    use_regex: bool = False,
    include_patterns: Optional[str] = None,
    exclude_patterns: Optional[str] = None,
    file_types: str = "all",
    max_results: int = 1000,
    context_lines: int = 2,
    show_hidden: bool = False
) -> str:
    """Implementation for VSCode-like search across files and directories"""
    try:
        base_path = Path(search_path).expanduser().resolve()
        if not base_path.exists():
            return f"❌ Path '{search_path}' does not exist"
        
        # Prepare search pattern
        search_flags = 0 if case_sensitive else re.IGNORECASE
        
        if use_regex:
            try:
                pattern_str = r'\b' + search_term + r'\b' if whole_word else search_term
                pattern = re.compile(pattern_str, search_flags)
            except re.error as e:
                return f"❌ Invalid regex pattern: {e}"
        else:
            escaped_term = re.escape(search_term)
            pattern_str = r'\b' + escaped_term + r'\b' if whole_word else escaped_term
            pattern = re.compile(pattern_str, search_flags)
        
        # Prepare file patterns
        if include_patterns:
            include_list = [p.strip() for p in include_patterns.split(',')]
        elif file_types in FILE_TYPE_GROUPS:
            include_list = FILE_TYPE_GROUPS[file_types]
        else:
            include_list = [f"*.{p.strip()}" for p in file_types.split(',')] if file_types != "all" else ["*"]
        
        exclude_list = DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude_list.extend([p.strip() for p in exclude_patterns.split(',')])
        
        # Search files
        matches = []
        files_searched = 0
        files_with_matches = 0
        
        # Walk through directory
        for root, dirs, files in os.walk(base_path, topdown=True):
            root_path = Path(root)
            
            # Filter directories based on exclude patterns and hidden flag
            dirs[:] = [d for d in dirs if not should_exclude_file(root_path / d, exclude_list) and (show_hidden or not d.startswith('.'))]

            for file_name in files:
                if not show_hidden and file_name.startswith('.'):
                    continue
                
                file_path = root_path / file_name
                
                if not any(fnmatch.fnmatch(file_name, p) for p in include_list):
                    continue
                
                if should_exclude_file(file_path, exclude_list):
                    continue
                
                if not is_text_file(file_path):
                    continue
                
                files_searched += 1
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    file_has_match = False
                    for line_num, line in enumerate(lines, 1):
                        for match_obj in pattern.finditer(line):
                            start_line = max(0, line_num - context_lines - 1)
                            end_line = min(len(lines), line_num + context_lines)
                            context = [f"{'   ' if i != line_num - 1 else '>> '}{i+1:4d}: {lines[i].rstrip()}" for i in range(start_line, end_line)]
                            
                            match = SearchMatch(
                                file_path=str(file_path.relative_to(base_path)),
                                line_number=line_num,
                                column=match_obj.start() + 1,
                                line_content=line.strip(),
                                context_lines=context
                            )
                            matches.append(match)
                            file_has_match = True
                            if len(matches) >= max_results:
                                break
                    if file_has_match:
                        files_with_matches += 1
                except Exception:
                    continue

                if len(matches) >= max_results:
                    break
            if len(matches) >= max_results:
                break
        
        # Format results
        if not matches:
            return f"🔍 No matches found for '{search_term}' in {files_searched} files"
        
        result = f"🔍 **Search Results for '{search_term}'**\n"
        result += f"Found {len(matches)} matches in {files_with_matches} files (searched {files_searched} files)\n\n"
        
        files_dict = {}
        for match in matches:
            if match.file_path not in files_dict:
                files_dict[match.file_path] = []
            files_dict[match.file_path].append(match)
        
        for file_path, file_matches in files_dict.items():
            result += f"📄 **{file_path}** ({len(file_matches)} matches)\n"
            for match in file_matches:
                result += "\n".join(f"     {line}" for line in match.context_lines)
                result += "\n---\n"
        
        if len(matches) >= max_results:
            result += f"\n⚠️ Results limited to {max_results} matches. Consider refining your search."
            
        return result.strip()
        
    except Exception as e:
        return f"❌ Search error: {str(e)}"


# --- MCP Tool Registration ---

def register_search_tools(mcp: FastMCP):
    """Register advanced search tools with the MCP server."""
    
    @mcp.tool()
    def search_in_files(search_pattern: str, directory: str = ".", file_pattern: str = "*", use_regex: bool = False) -> str:
        """
        Search for a text pattern across multiple files (like grep).
        
        Args:
            search_pattern: The text or regex pattern to search for.
            directory: The directory to start searching from. Defaults to current directory.
            file_pattern: Glob pattern to match files (e.g., "*.py", "data*"). Defaults to all files.
            use_regex: Set to True to treat search_pattern as a regular expression.
        
        Returns:
            A string containing the file paths, line numbers, and content of matching lines.
        """
        return _search_in_files_impl(search_pattern=search_pattern, directory=directory, file_pattern=file_pattern, use_regex=use_regex)

    @mcp.tool()
    def search_adv(
        search_term: str,
        search_path: str = ".",
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False,
        include_patterns: Optional[str] = None,
        exclude_patterns: Optional[str] = None,
        file_types: str = "all",
        max_results: int = 1000,
        context_lines: int = 2,
        show_hidden: bool = False
    ) -> str:
        """
        Perform an advanced, VSCode-like search across files with extensive filtering.
        
        Args:
            search_term: The literal text or regex pattern to find.
            search_path: The root directory or file to search in.
            case_sensitive: If True, the search is case-sensitive.
            whole_word: If True, matches only whole words.
            use_regex: If True, treats search_term as a regular expression.
            include_patterns: Comma-separated list of glob patterns for files to include (e.g., "*.py,*.md").
            exclude_patterns: Comma-separated list of glob patterns for files/dirs to exclude (e.g., "node_modules/*,*.log").
            file_types: A preset group ("py", "js", "web", "docs") or comma-separated extensions ("py,md,txt").
            max_results: The maximum number of individual matches to return.
            context_lines: Number of lines to show before and after the matching line.
            show_hidden: If True, searches in hidden files and directories (those starting with ".").

        Returns:
            A formatted string with detailed search results, including context for each match.
        """
        return _search_adv_impl(
            search_term=search_term, search_path=search_path, case_sensitive=case_sensitive,
            whole_word=whole_word, use_regex=use_regex, include_patterns=include_patterns,
            exclude_patterns=exclude_patterns, file_types=file_types, max_results=max_results,
            context_lines=context_lines, show_hidden=show_hidden
        )