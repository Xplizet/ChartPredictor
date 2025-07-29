"""
Export manager for ChartPredictor analysis results
Supports JSON, CSV, and PDF export formats
"""

import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from loguru import logger

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available. PDF export will be disabled.")


class ExportManager:
    """Handles exporting analysis results to various formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv']
        if REPORTLAB_AVAILABLE:
            self.supported_formats.append('pdf')
    
    def export_results(self, analysis_results: Dict[str, Any], 
                      export_path: str, format_type: str) -> bool:
        """Export analysis results to specified format"""
        try:
            format_type = format_type.lower()
            
            if format_type not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format_type}. "
                               f"Supported formats: {', '.join(self.supported_formats)}")
            
            # Ensure directory exists
            Path(export_path).parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == 'json':
                return self._export_json(analysis_results, export_path)
            elif format_type == 'csv':
                return self._export_csv(analysis_results, export_path)
            elif format_type == 'pdf':
                return self._export_pdf(analysis_results, export_path)
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def _export_json(self, results: Dict[str, Any], file_path: str) -> bool:
        """Export results as JSON file"""
        try:
            # Convert dataclass objects to dictionaries
            exportable_results = self._prepare_data_for_export(results)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(exportable_results, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Results exported to JSON: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False
    
    def _export_csv(self, results: Dict[str, Any], file_path: str) -> bool:
        """Export results as CSV file"""
        try:
            # Create multiple CSV files for different data types
            base_path = Path(file_path)
            base_name = base_path.stem
            export_dir = base_path.parent
            
            # Export OHLC data
            if 'chart_data' in results and results['chart_data'] and hasattr(results['chart_data'], 'ohlc_data') and results['chart_data'].ohlc_data:
                ohlc_data = []
                for ohlc in results['chart_data'].ohlc_data:
                    ohlc_dict = asdict(ohlc) if hasattr(ohlc, '__dict__') else ohlc
                    ohlc_data.append(ohlc_dict)
                
                ohlc_df = pd.DataFrame(ohlc_data)
                ohlc_path = export_dir / f"{base_name}_ohlc_data.csv"
                ohlc_df.to_csv(ohlc_path, index=False)
            
            # Export technical indicators
            if 'technical_analysis' in results:
                tech_data = []
                for indicator, value in results['technical_analysis'].items():
                    tech_data.append({
                        'Indicator': indicator,
                        'Value': value,
                        'Timestamp': results.get('timestamp', datetime.now().isoformat())
                    })
                
                tech_df = pd.DataFrame(tech_data)
                tech_path = export_dir / f"{base_name}_technical_indicators.csv"
                tech_df.to_csv(tech_path, index=False)
            
            # Export patterns and predictions summary
            summary_data = []
            
            # Add basic info
            summary_data.append({
                'Category': 'General',
                'Item': 'Symbol',
                'Value': results.get('symbol', 'N/A'),
                'Confidence': '',
                'Description': ''
            })
            
            summary_data.append({
                'Category': 'General',
                'Item': 'Data Source',
                'Value': results.get('data_source', 'N/A'),
                'Confidence': '',
                'Description': ''
            })
            
            # Add patterns
            if 'patterns' in results and results['patterns']:
                for pattern in results['patterns']:
                    pattern_dict = asdict(pattern) if hasattr(pattern, '__dict__') else pattern
                    summary_data.append({
                        'Category': 'Pattern',
                        'Item': pattern_dict.get('name', 'Unknown'),
                        'Value': pattern_dict.get('pattern_type', 'N/A'),
                        'Confidence': f"{pattern_dict.get('confidence', 0):.1%}",
                        'Description': pattern_dict.get('description', '')
                    })
            
            # Add predictions
            if 'predictions' in results and results['predictions']:
                pred = results['predictions']
                pred_dict = asdict(pred) if hasattr(pred, '__dict__') else pred
                summary_data.append({
                    'Category': 'Prediction',
                    'Item': 'Direction',
                    'Value': pred_dict.get('direction', 'N/A'),
                    'Confidence': f"{pred_dict.get('confidence', 0):.1%}",
                    'Description': pred_dict.get('reasoning', '')
                })
                
                summary_data.append({
                    'Category': 'Prediction',
                    'Item': 'Target Price',
                    'Value': pred_dict.get('target_price', 'N/A'),
                    'Confidence': '',
                    'Description': f"Time Horizon: {pred_dict.get('time_horizon', 'N/A')}"
                })
            
            # Add trading signals
            if 'signals' in results and results['signals']:
                signal = results['signals']
                signal_dict = asdict(signal) if hasattr(signal, '__dict__') else signal
                summary_data.append({
                    'Category': 'Trading Signal',
                    'Item': 'Action',
                    'Value': signal_dict.get('action', 'N/A'),
                    'Confidence': signal_dict.get('strength', 'N/A'),
                    'Description': f"Entry: {signal_dict.get('entry_price', 'N/A')}, "
                                 f"Stop: {signal_dict.get('stop_loss', 'N/A')}, "
                                 f"Target: {signal_dict.get('take_profit', 'N/A')}"
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_path = export_dir / f"{base_name}_analysis_summary.csv"
            summary_df.to_csv(summary_path, index=False)
            
            logger.info(f"Results exported to CSV files in: {export_dir}")
            return True
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
    
    def _export_pdf(self, results: Dict[str, Any], file_path: str) -> bool:
        """Export results as PDF report"""
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available for PDF export")
            return False
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            symbol = results.get('symbol', 'Unknown Symbol')
            story.append(Paragraph(f"ChartPredictor Analysis Report - {symbol}", title_style))
            story.append(Spacer(1, 20))
            
            # Analysis metadata
            story.append(Paragraph("Analysis Overview", styles['Heading2']))
            
            metadata_data = [
                ['Symbol', results.get('symbol', 'N/A')],
                ['Data Source', results.get('data_source', 'N/A')],
                ['Analysis Time', results.get('timestamp', 'N/A')],
                ['Data Points', str(len(getattr(results.get('chart_data', None), 'ohlc_data', []))) if 'chart_data' in results and results['chart_data'] else 'N/A']
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metadata_table)
            story.append(Spacer(1, 20))
            
            # Technical Indicators
            if 'technical_analysis' in results and results['technical_analysis']:
                story.append(Paragraph("Technical Indicators", styles['Heading2']))
                
                tech_data = [['Indicator', 'Value']]
                for indicator, value in results['technical_analysis'].items():
                    if isinstance(value, (int, float)):
                        formatted_value = f"{value:.4f}" if abs(value) < 1 else f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    tech_data.append([indicator, formatted_value])
                
                tech_table = Table(tech_data, colWidths=[2.5*inch, 2.5*inch])
                tech_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(tech_table)
                story.append(Spacer(1, 20))
            
            # Detected Patterns
            if 'patterns' in results and results['patterns']:
                story.append(Paragraph("Detected Chart Patterns", styles['Heading2']))
                
                pattern_data = [['Pattern', 'Type', 'Confidence', 'Description']]
                for pattern in results['patterns']:
                    pattern_dict = asdict(pattern) if hasattr(pattern, '__dict__') else pattern
                    pattern_data.append([
                        pattern_dict.get('name', 'Unknown'),
                        pattern_dict.get('pattern_type', 'N/A'),
                        f"{pattern_dict.get('confidence', 0):.1%}",
                        pattern_dict.get('description', '')[:50] + '...' if len(pattern_dict.get('description', '')) > 50 else pattern_dict.get('description', '')
                    ])
                
                pattern_table = Table(pattern_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
                pattern_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(pattern_table)
                story.append(Spacer(1, 20))
            
            # Price Prediction
            if 'predictions' in results and results['predictions']:
                story.append(Paragraph("Price Movement Prediction", styles['Heading2']))
                
                pred = results['predictions']
                pred_dict = asdict(pred) if hasattr(pred, '__dict__') else pred
                
                pred_data = [
                    ['Direction', pred_dict.get('direction', 'N/A')],
                    ['Confidence', f"{pred_dict.get('confidence', 0):.1%}"],
                    ['Target Price', str(pred_dict.get('target_price', 'N/A'))],
                    ['Time Horizon', pred_dict.get('time_horizon', 'N/A')],
                    ['Reasoning', pred_dict.get('reasoning', 'N/A')]
                ]
                
                pred_table = Table(pred_data, colWidths=[2*inch, 3*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(pred_table)
                story.append(Spacer(1, 20))
            
            # Trading Signals
            if 'signals' in results and results['signals']:
                story.append(Paragraph("Trading Recommendations", styles['Heading2']))
                
                signal = results['signals']
                signal_dict = asdict(signal) if hasattr(signal, '__dict__') else signal
                
                signal_data = [
                    ['Action', signal_dict.get('action', 'N/A')],
                    ['Signal Strength', signal_dict.get('strength', 'N/A')],
                    ['Entry Price', str(signal_dict.get('entry_price', 'N/A'))],
                    ['Stop Loss', str(signal_dict.get('stop_loss', 'N/A'))],
                    ['Take Profit', str(signal_dict.get('take_profit', 'N/A'))],
                    ['Risk/Reward Ratio', str(signal_dict.get('risk_reward_ratio', 'N/A'))]
                ]
                
                signal_table = Table(signal_data, colWidths=[2*inch, 3*inch])
                signal_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(signal_table)
                story.append(Spacer(1, 20))
            
            # Disclaimer
            story.append(Paragraph("Disclaimer", styles['Heading3']))
            disclaimer_text = ("This analysis is for informational purposes only and should not be "
                             "considered as financial advice. Trading involves risk and you should "
                             "consult with a qualified financial advisor before making investment decisions.")
            story.append(Paragraph(disclaimer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report exported: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return False
    
    def _prepare_data_for_export(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dataclass objects to dictionaries for JSON serialization"""
        exportable_results = {}
        
        for key, value in results.items():
            if hasattr(value, '__dict__'):  # Dataclass or object
                if hasattr(value, 'ohlc_data'):  # ChartData object
                    exportable_results[key] = {
                        'ohlc_data': [asdict(ohlc) for ohlc in value.ohlc_data],
                        'price_levels': value.price_levels,
                        'timeframe': value.timeframe,
                        'symbol': getattr(value, 'symbol', None),
                        'extraction_confidence': value.extraction_confidence
                    }
                elif isinstance(value, list):  # List of dataclass objects
                    exportable_results[key] = [asdict(item) if hasattr(item, '__dict__') else item for item in value]
                else:  # Single dataclass object
                    exportable_results[key] = asdict(value)
            elif isinstance(value, list):  # List that might contain dataclass objects
                exportable_results[key] = [asdict(item) if hasattr(item, '__dict__') else item for item in value]
            else:  # Regular value
                exportable_results[key] = value
        
        return exportable_results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return self.supported_formats.copy()