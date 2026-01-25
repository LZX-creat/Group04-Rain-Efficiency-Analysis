import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

class RainWorkbench:
    def __init__(self, root):
        self.root = root
        self.root.title("降雨量工作台")
        self.root.geometry("800x600")
        
        # 创建数据库连接
        self.conn = sqlite3.connect('rainfall.db')
        self.create_table()
        
        # 创建主界面
        self.create_main_window()
    
    def create_table(self):
        """创建降雨量数据表"""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rainfall_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT NOT NULL,
            rainfall REAL NOT NULL,
            notes TEXT
        )
        ''')
        self.conn.commit()
    
    def create_main_window(self):
        """创建主窗口和菜单"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        
        # 创建降雨量台账菜单
        record_menu = tk.Menu(menubar, tearoff=0)
        record_menu.add_command(label="添加记录", command=self.add_record)
        record_menu.add_command(label="查看记录", command=self.view_records)
        record_menu.add_command(label="导出记录", command=self.export_records)
        menubar.add_cascade(label="降雨量台账", menu=record_menu)
        
        # 创建降雨量统计中心菜单
        stats_menu = tk.Menu(menubar, tearoff=0)
        stats_menu.add_command(label="按日统计", command=lambda: self.statistics("day"))
        stats_menu.add_command(label="按月统计", command=lambda: self.statistics("month"))
        stats_menu.add_command(label="按年统计", command=lambda: self.statistics("year"))
        stats_menu.add_command(label="趋势分析", command=self.trend_analysis)
        menubar.add_cascade(label="降雨量统计中心", menu=stats_menu)
        
        # 配置菜单栏
        self.root.config(menu=menubar)
        
        # 创建主内容区域
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加欢迎信息
        welcome_label = ttk.Label(self.main_frame, text="欢迎使用降雨量工作台", font=("Arial", 16, "bold"))
        welcome_label.pack(pady=20)
        
        info_label = ttk.Label(self.main_frame, text="请从菜单栏选择功能", font=("Arial", 12))
        info_label.pack(pady=10)
    
    def add_record(self):
        """添加降雨量记录"""
        # 创建添加记录窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加降雨量记录")
        add_window.geometry("500x400")
        
        # 创建表单
        form_frame = ttk.Frame(add_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日期
        ttk.Label(form_frame, text="日期:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=10)
        date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form_frame, textvariable=date_var, width=25).grid(row=0, column=1, pady=10, padx=10)
        
        # 时间
        ttk.Label(form_frame, text="时间:").grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        time_var = tk.StringVar(value=datetime.datetime.now().strftime("%H:%M:%S"))
        ttk.Entry(form_frame, textvariable=time_var, width=25).grid(row=1, column=1, pady=10, padx=10)
        
        # 地点
        ttk.Label(form_frame, text="地点:").grid(row=2, column=0, sticky=tk.W, pady=10, padx=10)
        location_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=location_var, width=25).grid(row=2, column=1, pady=10, padx=10)
        
        # 降雨量
        ttk.Label(form_frame, text="降雨量 (mm):").grid(row=3, column=0, sticky=tk.W, pady=10, padx=10)
        rainfall_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=rainfall_var, width=25).grid(row=3, column=1, pady=10, padx=10)
        
        # 备注
        ttk.Label(form_frame, text="备注:").grid(row=4, column=0, sticky=tk.W, pady=10, padx=10)
        notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=notes_var, width=25).grid(row=4, column=1, pady=10, padx=10)
        
        # 保存按钮
        def save_record():
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                INSERT INTO rainfall_records (date, time, location, rainfall, notes)
                VALUES (?, ?, ?, ?, ?)
                ''', (date_var.get(), time_var.get(), location_var.get(), rainfall_var.get(), notes_var.get()))
                self.conn.commit()
                messagebox.showinfo("成功", "记录添加成功！")
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"添加记录失败: {str(e)}")
        
        ttk.Button(form_frame, text="保存", command=save_record, width=15).grid(row=5, column=0, columnspan=2, pady=20)
    
    def view_records(self):
        """查看降雨量记录"""
        # 创建查看记录窗口
        view_window = tk.Toplevel(self.root)
        view_window.title("查看降雨量记录")
        view_window.geometry("600x400")
        
        # 创建表格
        tree_frame = ttk.Frame(view_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        tree = ttk.Treeview(tree_frame, columns=("id", "date", "time", "location", "rainfall", "notes"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("date", text="日期")
        tree.heading("time", text="时间")
        tree.heading("location", text="地点")
        tree.heading("rainfall", text="降雨量 (mm)")
        tree.heading("notes", text="备注")
        
        # 设置列宽
        tree.column("id", width=50)
        tree.column("date", width=100)
        tree.column("time", width=100)
        tree.column("location", width=100)
        tree.column("rainfall", width=100)
        tree.column("notes", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 加载数据
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM rainfall_records ORDER BY date DESC, time DESC")
            records = cursor.fetchall()
            
            for record in records:
                tree.insert("", tk.END, values=record)
        except Exception as e:
            messagebox.showerror("错误", f"加载记录失败: {str(e)}")
    
    def export_records(self):
        """导出降雨量记录"""
        try:
            # 选择导出文件路径
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
            )
            
            if file_path:
                # 加载数据
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM rainfall_records ORDER BY date DESC, time DESC")
                records = cursor.fetchall()
                
                # 写入CSV文件
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # 写入表头
                    writer.writerow(["ID", "日期", "时间", "地点", "降雨量 (mm)", "备注"])
                    # 写入数据
                    for record in records:
                        writer.writerow(record)
                
                messagebox.showinfo("成功", "记录导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出记录失败: {str(e)}")
    
    def statistics(self, period):
        """按不同周期统计降雨量"""
        # 创建统计窗口
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"按{('日', '月', '年')[('day', 'month', 'year').index(period)]}统计降雨量")
        stats_window.geometry("600x400")
        
        # 创建统计结果区域
        result_frame = ttk.Frame(stats_window, padding="20")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 加载数据并统计
        try:
            cursor = self.conn.cursor()
            
            if period == "day":
                # 按日统计
                cursor.execute('''
                SELECT date, SUM(rainfall) as total_rainfall
                FROM rainfall_records
                GROUP BY date
                ORDER BY date DESC
                ''')
            elif period == "month":
                # 按月统计
                cursor.execute('''
                SELECT SUBSTR(date, 1, 7) as month, SUM(rainfall) as total_rainfall
                FROM rainfall_records
                GROUP BY month
                ORDER BY month DESC
                ''')
            else:  # year
                # 按年统计
                cursor.execute('''
                SELECT SUBSTR(date, 1, 4) as year, SUM(rainfall) as total_rainfall
                FROM rainfall_records
                GROUP BY year
                ORDER BY year DESC
                ''')
            
            stats = cursor.fetchall()
            
            # 创建表格
            tree = ttk.Treeview(result_frame, columns=("period", "total_rainfall"), show="headings")
            tree.heading("period", text=("日期", "月份", "年份")[('day', 'month', 'year').index(period)])
            tree.heading("total_rainfall", text="总降雨量 (mm)")
            
            tree.column("period", width=150)
            tree.column("total_rainfall", width=150)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)
            
            # 添加数据
            for stat in stats:
                tree.insert("", tk.END, values=stat)
            
            # 计算统计信息
            if stats:
                total_rainfall = sum(stat[1] for stat in stats)
                avg_rainfall = total_rainfall / len(stats)
                
                info_frame = ttk.Frame(result_frame, padding="10")
                info_frame.pack(fill=tk.X, pady=10)
                
                ttk.Label(info_frame, text=f"统计周期数: {len(stats)}").pack(side=tk.LEFT, padx=10)
                ttk.Label(info_frame, text=f"总降雨量: {total_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
                ttk.Label(info_frame, text=f"平均降雨量: {avg_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
        
        except Exception as e:
            messagebox.showerror("错误", f"统计失败: {str(e)}")
    
    def trend_analysis(self):
        """降雨量趋势分析"""
        # 创建趋势分析窗口
        trend_window = tk.Toplevel(self.root)
        trend_window.title("降雨量趋势分析")
        trend_window.geometry("800x500")
        
        # 创建分析区域
        analysis_frame = ttk.Frame(trend_window, padding="20")
        analysis_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            # 加载数据
            cursor = self.conn.cursor()
            cursor.execute("SELECT date, SUM(rainfall) as daily_rainfall FROM rainfall_records GROUP BY date ORDER BY date")
            records = cursor.fetchall()
            
            if not records:
                messagebox.showinfo("提示", "没有足够的数据进行趋势分析")
                return
            
            # 准备数据
            dates = [record[0] for record in records]
            rainfall = [record[1] for record in records]
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, rainfall, marker='o', linestyle='-', color='b')
            ax.set_title('降雨量趋势')
            ax.set_xlabel('日期')
            ax.set_ylabel('降雨量 (mm)')
            ax.grid(True)
            
            # 旋转日期标签
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 将图表嵌入到Tkinter窗口
            canvas = FigureCanvasTkAgg(fig, master=analysis_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # 计算统计信息
            total_rainfall = sum(rainfall)
            avg_rainfall = total_rainfall / len(rainfall)
            max_rainfall = max(rainfall)
            min_rainfall = min(rainfall)
            
            # 显示统计信息
            stats_frame = ttk.Frame(trend_window, padding="10")
            stats_frame.pack(fill=tk.X)
            
            ttk.Label(stats_frame, text=f"总降雨量: {total_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"平均降雨量: {avg_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"最大降雨量: {max_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"最小降雨量: {min_rainfall:.2f} mm").pack(side=tk.LEFT, padx=10)
        
        except Exception as e:
            messagebox.showerror("错误", f"趋势分析失败: {str(e)}")
    
    def __del__(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

if __name__ == "__main__":
    # 检查是否安装了matplotlib
    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except ImportError:
        print("请安装matplotlib库: pip install matplotlib")
        exit(1)
    
    # 创建主窗口
    root = tk.Tk()
    
    # 创建工作台实例
    app = RainWorkbench(root)
    
    # 运行主循环
    root.mainloop()