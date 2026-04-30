"""
PDF Report Generator for Trading Bot
Generates detailed PDF reports with strategy performance, win rates, and analysis
"""
from datetime import datetime
from typing import List, Dict
import json

class PDFReportGenerator:
    """Generate PDF reports for trading bot"""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_backtest_report(self, trades: List[Dict], stats: Dict, output_path: str):
        """Generate backtest PDF report"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.graphics.charts.lineplots import LinePlot
            from reportlab.graphics.shapes import Drawing
            import io
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1a1a1a'))
            story.append(Paragraph("MT5 Trading Bot - Backtest Report", title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Summary Section
            story.append(Paragraph("Summary", styles['Heading2']))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Symbol', stats.get('symbol', 'N/A')],
                ['Timeframe', stats.get('timeframe', 'N/A')],
                ['Period (Days)', str(stats.get('days', 0))],
                ['Total Trades', str(stats.get('total_trades', 0))],
                ['Winning Trades', str(stats.get('winning_trades', 0))],
                ['Losing Trades', str(stats.get('losing_trades', 0))],
                ['Win Rate', f"{stats.get('win_rate', 0):.2f}%"],
                ['Total Profit', f"${stats.get('total_profit', 0):.2f}"],
                ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.5*inch))
            
            # Strategy Configuration
            story.append(Paragraph("Strategy Configuration - ENB Model", styles['Heading2']))
            
            config = {
                "Name": "ENB Strategy (Engulfing + Structure + Liquidity)",
                "Market Structure": "Enabled - HH/HL for bullish, LH/LL for bearish",
                "Liquidity Sweep": "Enabled - Previous high/low sweep detection",
                "Engulfing Entry": "Enabled - Strong candle confirmation",
                "Risk per Trade": "1%",
                "Risk:Reward Ratio": "1:2"
            }
            
            config_data = [[k, v] for k, v in config.items()]
            config_table = Table(config_data, colWidths=[2*inch, 4*inch])
            config_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D0E4F7')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(config_table)
            story.append(Spacer(1, 0.5*inch))
            
            # Trades List (last 20)
            story.append(Paragraph("Recent Trades (Last 20)", styles['Heading2']))
            
            if trades:
                trades_data = [['#', 'Time', 'Signal', 'Entry', 'Exit', 'Profit', 'Confidence']]
                for i, trade in enumerate(trades[-20:], 1):
                    trades_data.append([
                        str(i),
                        trade['entry_time'].strftime('%Y-%m-%d %H:%M') if hasattr(trade['entry_time'], 'strftime') else str(trade['entry_time']),
                        trade['signal'],
                        f"${trade['entry_price']:.5f}",
                        f"${trade.get('exit_price', 0):.5f}",
                        f"${trade.get('profit', 0):.2f}",
                        trade.get('confidence', 'N/A')
                    ])
                
                trades_table = Table(trades_data, colWidths=[0.5*inch, 1.2*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.9*inch])
                trades_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(trades_table)
            
            # Build PDF
            doc.build(story)
            print(f"✅ PDF report generated: {output_path}")
            
        except ImportError:
            print("❌ reportlab not installed. Install: pip install reportlab")
            print("   Generating text report instead...")
            self._generate_text_report(trades, stats, output_path.replace('.pdf', '.txt'))
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
    
    def generate_trading_report(self, signals: List[Dict], symbol: str, days: int, output_path: str):
        """Generate general trading activity report"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(f"Trading Report - {symbol}", styles['Heading1']))
            story.append(Spacer(1, 0.3*inch))
            
            # Summary
            story.append(Paragraph(f"Period: Last {days} days", styles['Normal']))
            story.append(Paragraph(f"Total Signals: {len(signals)}", styles['Normal']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            
            story.append(Spacer(1, 0.5*inch))
            
            # Signals breakdown
            buy_signals = sum(1 for s in signals if s['signal'] == 'BUY')
            sell_signals = sum(1 for s in signals if s['signal'] == 'SELL')
            
            breakdown_data = [
                ['Metric', 'Count', 'Percentage'],
                ['BUY Signals', str(buy_signals), f"{buy_signals/len(signals)*100:.1f}%" if signals else "0%"],
                ['SELL Signals', str(sell_signals), f"{sell_signals/len(signals)*100:.1f}%" if signals else "0%"],
                ['Total', str(len(signals)), "100%"]
            ]
            
            breakdown_table = Table(breakdown_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(breakdown_table)
            
            doc.build(story)
            print(f"✅ Trading report generated: {output_path}")
            
        except ImportError:
            print("❌ reportlab not installed. Install: pip install reportlab")
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def _generate_text_report(self, trades: List[Dict], stats: Dict, output_path: str):
        """Fallback text report if PDF generation fails"""
        with open(output_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("MT5 Trading Bot - Backtest Report (Text)\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Symbol: {stats.get('symbol', 'N/A')}\n")
            f.write(f"Timeframe: {stats.get('timeframe', 'N/A')}\n")
            f.write(f"Total Trades: {stats.get('total_trades', 0)}\n")
            f.write(f"Winning Trades: {stats.get('winning_trades', 0)}\n")
            f.write(f"Losing Trades: {stats.get('losing_trades', 0)}\n")
            f.write(f"Win Rate: {stats.get('win_rate', 0):.2f}%\n")
            f.write(f"Total Profit: ${stats.get('total_profit', 0):.2f}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            f.write("\nSTRATEGY: ENB (Engulfing + Structure + Liquidity)\n")
            f.write("-" * 40 + "\n")
            f.write("Market Structure: HH/HL (bullish), LH/LL (bearish)\n")
            f.write("Liquidity Sweep: Previous high/low detection\n")
            f.write("Engulfing Entry: Strong candle confirmation\n")
            
            f.write("\nRECENT TRADES (Last 20)\n")
            f.write("-" * 40 + "\n")
            for i, trade in enumerate(trades[-20:], 1):
                f.write(f"{i}. {trade.get('signal', 'N/A')} @ ${trade.get('entry_price', 0):.5f} | "
                       f"Profit: ${trade.get('profit', 0):.2f} | "
                       f"Confidence: {trade.get('confidence', 'N/A')}\n")
        
        print(f"✅ Text report generated: {output_path}")
