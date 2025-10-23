"""
Email Templates for Petition Management System
"""

def get_high_urgency_alert_template(petition_data):
    """High urgency petition alert email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
            }}
            .header {{
                background: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .alert-badge {{
                display: inline-block;
                background: #fff;
                color: #f72585;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .urgency-banner {{
                background: #fff3cd;
                border-left: 4px solid #f72585;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .info-card {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #dee2e6;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: bold;
                color: #6c757d;
            }}
            .info-value {{
                color: #212529;
            }}
            .description-box {{
                background: #ffffff;
                border: 2px solid #f72585;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }}
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 HIGH URGENCY PETITION ALERT</h1>
                <div class="alert-badge">IMMEDIATE ATTENTION REQUIRED</div>
            </div>
            
            <div class="content">
                <div class="urgency-banner">
                    <strong>⚠️ Alert:</strong> A high-priority petition has been submitted and requires immediate attention from your department.
                </div>
                
                <div class="info-card">
                    <div class="info-row">
                        <span class="info-label">Ticket ID:</span>
                        <span class="info-value"><strong>{petition_data.get('ticket_id', 'N/A')}</strong></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Department:</span>
                        <span class="info-value">{petition_data.get('department', 'N/A')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Category:</span>
                        <span class="info-value">{petition_data.get('category', 'N/A')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Submitted By:</span>
                        <span class="info-value">{petition_data.get('name', 'N/A')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Contact:</span>
                        <span class="info-value">{petition_data.get('email', 'N/A')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Submitted On:</span>
                        <span class="info-value">{petition_data.get('created_at', 'N/A')}</span>
                    </div>
                </div>
                
                <h3 style="color: #f72585;">Petition Title:</h3>
                <p style="font-size: 16px; font-weight: bold;">{petition_data.get('title', 'N/A')}</p>
                
                <h3 style="color: #f72585;">Description:</h3>
                <div class="description-box">
                    {petition_data.get('description', 'N/A')}
                </div>
                
                <div style="text-align: center;">
                    <a href="http://127.0.0.1:5000/department-dashboard.html" class="action-button">
                        View Petition Dashboard
                    </a>
                </div>
                
                <p style="margin-top: 30px; color: #6c757d; font-size: 14px;">
                    <strong>Note:</strong> This petition has been flagged as high urgency based on its content and requires prompt action.
                </p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from the Petition Management System</p>
                <p>© 2025 Petition Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_daily_summary_template(summary_data):
    """Daily summary email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
            }}
            .header {{
                background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .date-badge {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 8px 16px;
                border-radius: 20px;
                margin-top: 10px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-left: 4px solid #4361ee;
                padding: 15px;
                border-radius: 8px;
            }}
            .stat-card.warning {{
                border-left-color: #f8961e;
            }}
            .stat-card.success {{
                border-left-color: #4cc9f0;
            }}
            .stat-card.danger {{
                border-left-color: #f72585;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                color: #212529;
            }}
            .stat-label {{
                font-size: 14px;
                color: #6c757d;
                margin-top: 5px;
            }}
            .section {{
                margin: 30px 0;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #4361ee;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e9ecef;
            }}
            .petition-item {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 3px solid #4361ee;
            }}
            .petition-title {{
                font-weight: bold;
                color: #212529;
            }}
            .petition-meta {{
                font-size: 12px;
                color: #6c757d;
                margin-top: 5px;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }}
            .badge-high {{
                background: #f72585;
                color: white;
            }}
            .badge-medium {{
                background: #f8961e;
                color: white;
            }}
            .badge-low {{
                background: #4cc9f0;
                color: white;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Daily Petition Summary</h1>
                <div class="date-badge">{summary_data.get('date', 'Today')}</div>
            </div>
            
            <div class="content">
                <h2 style="color: #4361ee;">Good day, {summary_data.get('department_name', 'Team')}!</h2>
                <p>Here's your daily petition activity summary:</p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{summary_data.get('new_petitions', 0)}</div>
                        <div class="stat-label">New Petitions</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-value">{summary_data.get('resolved_today', 0)}</div>
                        <div class="stat-label">Resolved Today</div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-value">{summary_data.get('pending', 0)}</div>
                        <div class="stat-label">Pending</div>
                    </div>
                    <div class="stat-card danger">
                        <div class="stat-value">{summary_data.get('high_urgency', 0)}</div>
                        <div class="stat-label">High Urgency</div>
                    </div>
                </div>
                
                {_render_petition_list(summary_data.get('high_urgency_petitions', []), 'High Priority Petitions')}
                {_render_petition_list(summary_data.get('new_today', []), 'New Petitions Today')}
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://127.0.0.1:5000/department-dashboard.html" 
                       style="display: inline-block; background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); 
                              color: white; padding: 12px 30px; text-decoration: none; 
                              border-radius: 25px; font-weight: bold;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is your automated daily summary from the Petition Management System</p>
                <p>© 2025 Petition Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_weekly_report_template(report_data):
    """Weekly performance report email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
            }}
            .header {{
                background: linear-gradient(135deg, #7209b7 0%, #4cc9f0 100%);
                color: white;
                padding: 40px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .week-badge {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 8px 16px;
                border-radius: 20px;
                margin-top: 10px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .performance-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }}
            .performance-card {{
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border: 2px solid #e9ecef;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
            }}
            .performance-value {{
                font-size: 36px;
                font-weight: bold;
                background: linear-gradient(135deg, #7209b7 0%, #4cc9f0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .performance-label {{
                font-size: 14px;
                color: #6c757d;
                margin-top: 10px;
            }}
            .trend-indicator {{
                font-size: 14px;
                margin-top: 5px;
            }}
            .trend-up {{
                color: #4cc9f0;
            }}
            .trend-down {{
                color: #f72585;
            }}
            .chart-section {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
            }}
            .bar-chart {{
                margin: 20px 0;
            }}
            .bar-item {{
                margin: 15px 0;
            }}
            .bar-label {{
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }}
            .bar-container {{
                background: #e9ecef;
                height: 30px;
                border-radius: 15px;
                overflow: hidden;
            }}
            .bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, #7209b7 0%, #4cc9f0 100%);
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 10px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            .insights {{
                background: #fff3cd;
                border-left: 4px solid #f8961e;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .insights-title {{
                font-weight: bold;
                color: #f8961e;
                margin-bottom: 10px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 Weekly Performance Report</h1>
                <div class="week-badge">{report_data.get('week_range', 'This Week')}</div>
            </div>
            
            <div class="content">
                <h2 style="color: #7209b7;">Hello {report_data.get('department_name', 'Team')}!</h2>
                <p>Here's your weekly performance summary and analytics:</p>
                
                <div class="performance-grid">
                    <div class="performance-card">
                        <div class="performance-value">{report_data.get('total_petitions', 0)}</div>
                        <div class="performance-label">Total Petitions</div>
                        <div class="trend-indicator trend-up">↑ {report_data.get('total_change', '+0')}% vs last week</div>
                    </div>
                    <div class="performance-card">
                        <div class="performance-value">{report_data.get('resolution_rate', 0)}%</div>
                        <div class="performance-label">Resolution Rate</div>
                        <div class="trend-indicator trend-up">↑ {report_data.get('resolution_change', '+0')}% improvement</div>
                    </div>
                    <div class="performance-card">
                        <div class="performance-value">{report_data.get('avg_response_time', '0')}h</div>
                        <div class="performance-label">Avg Response Time</div>
                        <div class="trend-indicator trend-up">↓ {report_data.get('response_change', '0')}h faster</div>
                    </div>
                    <div class="performance-card">
                        <div class="performance-value">{report_data.get('satisfaction_score', '0.0')}</div>
                        <div class="performance-label">Satisfaction Score</div>
                        <div class="trend-indicator trend-up">↑ {report_data.get('satisfaction_change', '+0.0')} points</div>
                    </div>
                </div>
                
                <div class="chart-section">
                    <h3 style="color: #7209b7; margin-top: 0;">Petition Status Breakdown</h3>
                    <div class="bar-chart">
                        {_render_bar_chart_item('Resolved', report_data.get('resolved', 0), report_data.get('total_petitions', 1))}
                        {_render_bar_chart_item('In Progress', report_data.get('in_progress', 0), report_data.get('total_petitions', 1))}
                        {_render_bar_chart_item('Pending', report_data.get('pending', 0), report_data.get('total_petitions', 1))}
                    </div>
                </div>
                
                <div class="insights">
                    <div class="insights-title">💡 Key Insights</div>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>{report_data.get('insight_1', 'Great work this week!')}</li>
                        <li>{report_data.get('insight_2', 'Keep up the excellent response times.')}</li>
                        <li>{report_data.get('insight_3', 'Focus on high-priority items.')}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://127.0.0.1:5000/department-analytics.html" 
                       style="display: inline-block; background: linear-gradient(135deg, #7209b7 0%, #4cc9f0 100%); 
                              color: white; padding: 12px 30px; text-decoration: none; 
                              border-radius: 25px; font-weight: bold;">
                        View Detailed Analytics
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>This is your automated weekly performance report</p>
                <p>© 2025 Petition Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def _render_petition_list(petitions, title):
    """Helper function to render petition list"""
    if not petitions:
        return ''
    
    html = f'<div class="section"><div class="section-title">{title}</div>'
    for petition in petitions[:5]:  # Limit to 5
        urgency_class = petition.get('urgency', 'low')
        html += f'''
        <div class="petition-item">
            <div class="petition-title">{petition.get('title', 'Untitled')}</div>
            <div class="petition-meta">
                <span class="badge badge-{urgency_class}">{urgency_class.upper()}</span>
                Ticket: {petition.get('ticket_id', 'N/A')} • 
                {petition.get('category', 'General')}
            </div>
        </div>
        '''
    html += '</div>'
    return html


def _render_bar_chart_item(label, value, total):
    """Helper function to render bar chart items"""
    percentage = int((value / total) * 100) if total > 0 else 0
    return f'''
    <div class="bar-item">
        <div class="bar-label">{label}</div>
        <div class="bar-container">
            <div class="bar-fill" style="width: {percentage}%;">{value}</div>
        </div>
    </div>
    '''


def get_deadline_reminder_template(petition_data, hours_remaining):
    """Deadline reminder email template for departments"""
    status_color = {
        'critical': '#f72585',  # less than 24 hours
        'warning': '#f8961e',   # less than 48 hours
        'info': '#4cc9f0'       # more than 48 hours
    }
    
    if hours_remaining < 24:
        urgency_level = 'critical'
        urgency_message = '⚠️ URGENT - Less than 24 hours remaining!'
    elif hours_remaining < 48:
        urgency_level = 'warning'
        urgency_message = '⏰ Warning - Less than 48 hours remaining'
    else:
        urgency_level = 'info'
        urgency_message = f'📅 Reminder - {int(hours_remaining / 24)} days remaining'
    
    color = status_color[urgency_level]
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background: #f5f7fb;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0 0 10px 0;
                font-size: 26px;
            }}
            .urgency-badge {{
                display: inline-block;
                background: #fff;
                color: {color};
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .deadline-box {{
                background: #fff3cd;
                border-left: 4px solid {color};
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .deadline-box h3 {{
                margin: 0 0 10px 0;
                color: {color};
                font-size: 18px;
            }}
            .petition-details {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .detail-row {{
                display: flex;
                padding: 8px 0;
                border-bottom: 1px solid #e0e0e0;
            }}
            .detail-row:last-child {{
                border-bottom: none;
            }}
            .detail-label {{
                font-weight: 600;
                width: 140px;
                color: #555;
            }}
            .detail-value {{
                flex: 1;
                color: #333;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
                color: white;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
                text-align: center;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Petition Deadline Reminder</h1>
                <div class="urgency-badge">{urgency_message}</div>
            </div>
            
            <div class="content">
                <p>Dear {petition_data.get('department', 'Department')} Team,</p>
                
                <p>This is a reminder that the following petition is approaching its deadline and requires your attention:</p>
                
                <div class="deadline-box">
                    <h3>⏰ Deadline Alert</h3>
                    <p style="margin: 0; font-size: 16px;">
                        <strong>{hours_remaining:.1f} hours</strong> remaining until deadline
                    </p>
                </div>
                
                <div class="petition-details">
                    <h3 style="margin-top: 0; color: #333;">Petition Details</h3>
                    
                    <div class="detail-row">
                        <div class="detail-label">Ticket ID:</div>
                        <div class="detail-value"><strong>{petition_data.get('ticket_id', 'N/A')}</strong></div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Title:</div>
                        <div class="detail-value">{petition_data.get('title', 'N/A')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Category:</div>
                        <div class="detail-value">{petition_data.get('category', 'N/A')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Urgency:</div>
                        <div class="detail-value"><strong>{petition_data.get('urgency', 'N/A').upper()}</strong></div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Status:</div>
                        <div class="detail-value">{petition_data.get('status', 'N/A').replace('_', ' ').title()}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Submitted By:</div>
                        <div class="detail-value">{petition_data.get('full_name', 'N/A')}</div>
                    </div>
                </div>
                
                <p><strong>Action Required:</strong> Please review and update the status of this petition as soon as possible to meet the deadline.</p>
                
                <center>
                    <a href="http://localhost:5000/department-dashboard.html" class="cta-button">
                        View Petition Dashboard →
                    </a>
                </center>
                
                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>Note:</strong> Meeting deadlines ensures timely resolution of citizen concerns and maintains system efficiency.
                </p>
            </div>
            
            <div class="footer">
                <p>This is an automated reminder from the Petition Management System.</p>
                <p style="margin: 5px 0;">© 2025 Petition Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_rejection_email_template(petition_data, rejection_reason):
    """Petition rejection notification email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
            }}
            .header {{
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .status-badge {{
                display: inline-block;
                background: #fff;
                color: #e74c3c;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                margin-top: 10px;
                font-size: 14px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .rejection-banner {{
                background: #fee;
                border-left: 4px solid #e74c3c;
                padding: 20px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .rejection-banner h3 {{
                margin: 0 0 10px 0;
                color: #e74c3c;
                font-size: 18px;
            }}
            .rejection-reason {{
                background: #fff;
                border: 1px solid #e74c3c;
                padding: 15px;
                border-radius: 6px;
                margin: 15px 0;
                color: #555;
                line-height: 1.8;
            }}
            .info-card {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .info-row {{
                display: flex;
                padding: 10px 0;
                border-bottom: 1px solid #dee2e6;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: 600;
                color: #495057;
                width: 150px;
            }}
            .info-value {{
                color: #212529;
                flex: 1;
            }}
            .action-section {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
            }}
            .action-section h3 {{
                margin: 0 0 15px 0;
                color: #495057;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 10px;
                transition: transform 0.3s;
            }}
            .btn:hover {{
                transform: translateY(-2px);
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 14px;
            }}
            .note {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Petition Status Update</h1>
                <div class="status-badge">REJECTED</div>
            </div>
            
            <div class="content">
                <p>Dear {petition_data.get('full_name', 'User')},</p>
                
                <p>We regret to inform you that your petition has been <strong>rejected</strong> by the {petition_data.get('department', 'relevant department')}.</p>
                
                <div class="rejection-banner">
                    <h3>🔍 Rejection Details</h3>
                    <p style="margin: 5px 0;"><strong>Your petition was carefully reviewed, and the department has provided the following explanation:</strong></p>
                </div>
                
                <div class="rejection-reason">
                    {rejection_reason}
                </div>
                
                <div class="info-card">
                    <div class="info-row">
                        <div class="info-label">Ticket ID:</div>
                        <div class="info-value"><strong>{petition_data.get('ticket_id', 'N/A')}</strong></div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Title:</div>
                        <div class="info-value">{petition_data.get('title', 'N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Category:</div>
                        <div class="info-value">{petition_data.get('category', 'N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Department:</div>
                        <div class="info-value">{petition_data.get('department', 'N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Submitted:</div>
                        <div class="info-value">{petition_data.get('created_at', 'N/A')}</div>
                    </div>
                </div>
                
                <div class="note">
                    <strong>📌 What happens next?</strong><br>
                    • You can review the rejection reason in your dashboard<br>
                    • If you believe this decision needs reconsideration, you may submit a new petition with additional information<br>
                    • For questions, please contact the department directly
                </div>
                
                <div class="action-section">
                    <h3>📊 View Full Details</h3>
                    <p style="margin: 10px 0; color: #666;">Track your petition and view complete history</p>
                    <a href="http://127.0.0.1:5000/track-petition.html?ticket={petition_data.get('ticket_id', '')}" class="btn">
                        View Petition Details
                    </a>
                </div>
                
                <p style="margin-top: 30px; color: #666;">If you have any concerns regarding this decision, please feel free to reach out to us.</p>
                
                <p>Best regards,<br>
                <strong>Petition Management System</strong></p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">This is an automated notification. Please do not reply to this email.</p>
                <p style="margin: 5px 0;">© 2025 Petition Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

