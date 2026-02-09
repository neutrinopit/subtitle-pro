"""
Subtitle Parser Module
Handles parsing and formatting of different subtitle formats
"""

import pysrt
import webvtt
import re
from typing import List, Dict, Any
import chardet

class SubtitleEntry:
    """Represents a single subtitle entry"""
    def __init__(self, index: int, start_time: str, end_time: str, text: str):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'text': self.text
        }

class SubtitleParser:
    """Handles parsing of different subtitle formats"""
    
    @staticmethod
    def detect_encoding(file_content: bytes) -> str:
        """Detect file encoding"""
        result = chardet.detect(file_content)
        return result['encoding'] or 'utf-8'
    
    @staticmethod
    def parse_srt(file_content: str) -> List[SubtitleEntry]:
        """Parse SRT format"""
        entries = []
        try:
            subs = pysrt.from_string(file_content)
            for i, sub in enumerate(subs, 1):
                entry = SubtitleEntry(
                    index=i,
                    start_time=str(sub.start),
                    end_time=str(sub.end),
                    text=sub.text
                )
                entries.append(entry)
        except Exception as e:
            raise ValueError(f"Error parsing SRT file: {str(e)}")
        return entries
    
    @staticmethod
    def parse_vtt(file_content: str) -> List[SubtitleEntry]:
        """Parse WebVTT format"""
        entries = []
        try:
            # Remove VTT header
            content = re.sub(r'WEBVTT.*?\n\n', '', file_content, flags=re.DOTALL)
            
            # Parse captions
            pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\Z)'
            matches = re.finditer(pattern, content, re.DOTALL)
            
            for i, match in enumerate(matches, 1):
                entry = SubtitleEntry(
                    index=i,
                    start_time=match.group(1),
                    end_time=match.group(2),
                    text=match.group(3).strip()
                )
                entries.append(entry)
        except Exception as e:
            raise ValueError(f"Error parsing VTT file: {str(e)}")
        return entries
    
    @staticmethod
    def parse_sbv(file_content: str) -> List[SubtitleEntry]:
        """Parse YouTube SBV format"""
        entries = []
        try:
            pattern = r'(\d+:\d+:\d+\.\d+),(\d+:\d+:\d+\.\d+)\n(.*?)(?=\n\n|\Z)'
            matches = re.finditer(pattern, file_content, re.DOTALL)
            
            for i, match in enumerate(matches, 1):
                entry = SubtitleEntry(
                    index=i,
                    start_time=match.group(1),
                    end_time=match.group(2),
                    text=match.group(3).strip()
                )
                entries.append(entry)
        except Exception as e:
            raise ValueError(f"Error parsing SBV file: {str(e)}")
        return entries
    
    @staticmethod
    def parse_ass(file_content: str) -> List[SubtitleEntry]:
        """Parse Advanced SubStation format"""
        entries = []
        try:
            # Find the Events section
            events_match = re.search(r'\[Events\].*?Format:(.*?)\n(.*)', file_content, re.DOTALL)
            if not events_match:
                raise ValueError("No Events section found")
            
            format_line = events_match.group(1).strip()
            events_content = events_match.group(2)
            
            # Parse format
            format_fields = [f.strip() for f in format_line.split(',')]
            start_idx = format_fields.index('Start')
            end_idx = format_fields.index('End')
            text_idx = format_fields.index('Text')
            
            # Parse dialogues
            dialogue_pattern = r'Dialogue:(.*?)(?=\nDialogue:|\Z)'
            matches = re.finditer(dialogue_pattern, events_content, re.DOTALL)
            
            for i, match in enumerate(matches, 1):
                fields = match.group(1).split(',', len(format_fields) - 1)
                if len(fields) >= len(format_fields):
                    entry = SubtitleEntry(
                        index=i,
                        start_time=fields[start_idx].strip(),
                        end_time=fields[end_idx].strip(),
                        text=fields[text_idx].strip()
                    )
                    entries.append(entry)
        except Exception as e:
            raise ValueError(f"Error parsing ASS file: {str(e)}")
        return entries
    
    @staticmethod
    def parse_sub(file_content: str) -> List[SubtitleEntry]:
        """Parse SubViewer format"""
        entries = []
        try:
            pattern = r'(\d{2}:\d{2}:\d{2}\.\d{2}),(\d{2}:\d{2}:\d{2}\.\d{2})\n(.*?)(?=\n\n|\Z)'
            matches = re.finditer(pattern, file_content, re.DOTALL)
            
            for i, match in enumerate(matches, 1):
                entry = SubtitleEntry(
                    index=i,
                    start_time=match.group(1),
                    end_time=match.group(2),
                    text=match.group(3).strip().replace('[br]', '\n')
                )
                entries.append(entry)
        except Exception as e:
            raise ValueError(f"Error parsing SUB file: {str(e)}")
        return entries
    
    @staticmethod
    def parse(file_content: bytes, file_format: str) -> List[SubtitleEntry]:
        """Parse subtitle file based on format"""
        encoding = SubtitleParser.detect_encoding(file_content)
        content = file_content.decode(encoding)
        
        parsers = {
            'srt': SubtitleParser.parse_srt,
            'vtt': SubtitleParser.parse_vtt,
            'sbv': SubtitleParser.parse_sbv,
            'ass': SubtitleParser.parse_ass,
            'sub': SubtitleParser.parse_sub,
            'stl': SubtitleParser.parse_srt  # STL often similar to SRT
        }
        
        parser = parsers.get(file_format.lower())
        if not parser:
            raise ValueError(f"Unsupported format: {file_format}")
        
        return parser(content)
    
    @staticmethod
    def format_srt(entries: List[SubtitleEntry]) -> str:
        """Format entries to SRT"""
        output = []
        for entry in entries:
            output.append(f"{entry.index}")
            output.append(f"{entry.start_time} --> {entry.end_time}")
            output.append(entry.text)
            output.append("")
        return "\n".join(output)
    
    @staticmethod
    def format_vtt(entries: List[SubtitleEntry]) -> str:
        """Format entries to WebVTT"""
        output = ["WEBVTT", ""]
        for entry in entries:
            output.append(f"{entry.start_time} --> {entry.end_time}")
            output.append(entry.text)
            output.append("")
        return "\n".join(output)
    
    @staticmethod
    def format_output(entries: List[SubtitleEntry], output_format: str) -> str:
        """Format entries to specified format"""
        formatters = {
            'srt': SubtitleParser.format_srt,
            'vtt': SubtitleParser.format_vtt,
        }
        
        formatter = formatters.get(output_format.lower(), SubtitleParser.format_srt)
        return formatter(entries)
