#!/usr/bin/env python3
"""
Database monitoring script for Recipe App
Monitors database performance and connection usage under load
"""

import psycopg2
import time
import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.database.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

class DatabaseMonitor:
    def __init__(self):
        self.connection_params = {
            'host': DATABASE_HOST,
            'port': DATABASE_PORT,
            'database': DATABASE_NAME,
            'user': DATABASE_USER,
            'password': DATABASE_PASSWORD
        }
    
    def get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def get_connection_stats(self):
        """Get current connection statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get connection count by database
            cursor.execute("""
                SELECT 
                    datname,
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted
                FROM pg_stat_database 
                WHERE datname = %s
            """, (DATABASE_NAME,))
            
            db_stats = cursor.fetchone()
            
            # Get active connections
            cursor.execute("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections,
                    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                FROM pg_stat_activity 
                WHERE datname = %s
            """, (DATABASE_NAME,))
            
            connection_stats = cursor.fetchone()
            
            # Get slow queries (if pg_stat_statements is available)
            slow_queries = []
            try:
                cursor.execute("""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE query LIKE '%recipe%'
                    ORDER BY mean_time DESC 
                    LIMIT 5
                """)
                slow_queries = cursor.fetchall()
            except psycopg2.Error:
                # pg_stat_statements not available
                pass
            
            cursor.close()
            conn.close()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'database_stats': {
                    'datname': db_stats[0] if db_stats else None,
                    'numbackends': db_stats[1] if db_stats else 0,
                    'xact_commit': db_stats[2] if db_stats else 0,
                    'xact_rollback': db_stats[3] if db_stats else 0,
                    'blks_read': db_stats[4] if db_stats else 0,
                    'blks_hit': db_stats[5] if db_stats else 0,
                    'tup_returned': db_stats[6] if db_stats else 0,
                    'tup_fetched': db_stats[7] if db_stats else 0,
                    'tup_inserted': db_stats[8] if db_stats else 0,
                    'tup_updated': db_stats[9] if db_stats else 0,
                    'tup_deleted': db_stats[10] if db_stats else 0
                },
                'connection_stats': {
                    'total_connections': connection_stats[0] if connection_stats else 0,
                    'active_connections': connection_stats[1] if connection_stats else 0,
                    'idle_connections': connection_stats[2] if connection_stats else 0,
                    'idle_in_transaction': connection_stats[3] if connection_stats else 0
                },
                'slow_queries': [
                    {
                        'query': query[0][:100] + '...' if len(query[0]) > 100 else query[0],
                        'calls': query[1],
                        'total_time': query[2],
                        'mean_time': query[3],
                        'rows': query[4]
                    }
                    for query in slow_queries
                ]
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_table_stats(self):
        """Get table statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    n_live_tup,
                    n_dead_tup,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables 
                ORDER BY n_live_tup DESC
            """)
            
            tables = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [
                {
                    'schema': table[0],
                    'table': table[1],
                    'inserts': table[2],
                    'updates': table[3],
                    'deletes': table[4],
                    'live_tuples': table[5],
                    'dead_tuples': table[6],
                    'last_vacuum': table[7].isoformat() if table[7] else None,
                    'last_autovacuum': table[8].isoformat() if table[8] else None,
                    'last_analyze': table[9].isoformat() if table[9] else None,
                    'last_autoanalyze': table[10].isoformat() if table[10] else None
                }
                for table in tables
            ]
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_index_stats(self):
        """Get index statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
            """)
            
            indexes = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [
                {
                    'schema': index[0],
                    'table': index[1],
                    'index': index[2],
                    'scans': index[3],
                    'tuples_read': index[4],
                    'tuples_fetched': index[5]
                }
                for index in indexes
            ]
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_lock_info(self):
        """Get current lock information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    l.pid,
                    l.mode,
                    l.granted,
                    a.usename,
                    a.application_name,
                    a.client_addr,
                    a.state,
                    a.query
                FROM pg_locks l
                JOIN pg_stat_activity a ON l.pid = a.pid
                WHERE l.database = (SELECT oid FROM pg_database WHERE datname = %s)
                AND l.mode NOT LIKE 'AccessShare%'
                ORDER BY l.pid
            """, (DATABASE_NAME,))
            
            locks = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [
                {
                    'pid': lock[0],
                    'mode': lock[1],
                    'granted': lock[2],
                    'username': lock[3],
                    'application': lock[4],
                    'client_addr': lock[5],
                    'state': lock[6],
                    'query': lock[7][:100] + '...' if lock[7] and len(lock[7]) > 100 else lock[7]
                }
                for lock in locks
            ]
            
        except Exception as e:
            return {'error': str(e)}
    
    def print_stats(self, stats):
        """Print statistics in a formatted way"""
        print(f"\n📊 Database Monitor - {stats['timestamp']}")
        print("=" * 60)
        
        if 'error' in stats:
            print(f"❌ Error: {stats['error']}")
            return
        
        # Connection stats
        conn_stats = stats['connection_stats']
        print(f"🔗 Connections:")
        print(f"   Total: {conn_stats['total_connections']}")
        print(f"   Active: {conn_stats['active_connections']}")
        print(f"   Idle: {conn_stats['idle_connections']}")
        print(f"   Idle in Transaction: {conn_stats['idle_in_transaction']}")
        
        # Database stats
        db_stats = stats['database_stats']
        if db_stats['numbackends'] > 0:
            print(f"\n📈 Database Activity:")
            print(f"   Backends: {db_stats['numbackends']}")
            print(f"   Commits: {db_stats['xact_commit']}")
            print(f"   Rollbacks: {db_stats['xact_rollback']}")
            
            # Calculate cache hit ratio
            if db_stats['blks_read'] + db_stats['blks_hit'] > 0:
                cache_hit_ratio = (db_stats['blks_hit'] / (db_stats['blks_read'] + db_stats['blks_hit'])) * 100
                print(f"   Cache Hit Ratio: {cache_hit_ratio:.2f}%")
            
            print(f"   Tuples Returned: {db_stats['tup_returned']}")
            print(f"   Tuples Fetched: {db_stats['tup_fetched']}")
        
        # Slow queries
        if stats['slow_queries']:
            print(f"\n🐌 Slow Queries:")
            for i, query in enumerate(stats['slow_queries'], 1):
                print(f"   {i}. {query['query']}")
                print(f"      Calls: {query['calls']}, Mean Time: {query['mean_time']:.2f}ms")
    
    def monitor_continuously(self, interval=5, duration=None):
        """Monitor database continuously"""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        if duration:
            print(f"   Duration: {duration}s")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                current_time = time.time()
                
                # Check if we've exceeded duration
                if duration and (current_time - start_time) > duration:
                    print(f"\n⏰ Monitoring completed after {duration}s")
                    break
                
                # Get and print stats
                stats = self.get_connection_stats()
                self.print_stats(stats)
                
                # Wait for next iteration
                if iteration % 10 == 0:
                    print(f"\n💾 Saving detailed stats to file...")
                    self.save_detailed_stats()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Monitoring stopped by user")
    
    def save_detailed_stats(self):
        """Save detailed statistics to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"database_stats_{timestamp}.json"
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'connection_stats': self.get_connection_stats(),
            'table_stats': self.get_table_stats(),
            'index_stats': self.get_index_stats(),
            'lock_info': self.get_lock_info()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            print(f"   Saved to: {filename}")
        except Exception as e:
            print(f"   Error saving stats: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Monitor for Recipe App')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds')
    parser.add_argument('--duration', type=int, help='Monitoring duration in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
    
    args = parser.parse_args()
    
    monitor = DatabaseMonitor()
    
    if args.once:
        # Run once
        stats = monitor.get_connection_stats()
        monitor.print_stats(stats)
        
        if args.detailed:
            print(f"\n📋 Table Statistics:")
            table_stats = monitor.get_table_stats()
            for table in table_stats[:5]:  # Show top 5 tables
                print(f"   {table['table']}: {table['live_tuples']} live tuples")
            
            print(f"\n🔍 Index Statistics:")
            index_stats = monitor.get_index_stats()
            for index in index_stats[:5]:  # Show top 5 indexes
                print(f"   {index['index']}: {index['scans']} scans")
            
            print(f"\n🔒 Lock Information:")
            lock_info = monitor.get_lock_info()
            if lock_info:
                for lock in lock_info:
                    print(f"   PID {lock['pid']}: {lock['mode']} ({'granted' if lock['granted'] else 'waiting'})")
            else:
                print("   No locks found")
    else:
        # Continuous monitoring
        monitor.monitor_continuously(args.interval, args.duration)

if __name__ == "__main__":
    main()
