import os
import sys
import logging
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5

# Configure logging for the engineering track
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def initialize_mt5_session() -> bool:
    """Initializes the MetaTrader 5 terminal connection."""
    logger.info("Attempting to connect to MetaTrader 5 terminal...")
    
    # Initialize MT5 platform
    if not mt5.initialize():
        logger.error(f"MT5 Initialization failed. Error code: {mt5.last_error()}")
        return False
        
    logger.info("MT5 Terminal successfully connected.")
    return True

def verify_market_symbol(symbol: str) -> bool:
    """Checks if the target symbol is visible and available for trading."""
    # Ensure symbol is selected in MarketWatch
    selected = mt5.symbol_select(symbol, True)
    if not selected:
        logger.error(f"Symbol {symbol} could not be selected. Check broker symbol mapping.")
        return False
        
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.error(f"Symbol {symbol} not found on this broker server.")
        return False
        
    logger.info(f"Verified Symbol: {symbol} | Path: {symbol_info.path}")
    return True

def fetch_historical_m15_bars(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Downloads historical M15 bars from MetaTrader 5.
    Returns a clean structured pandas DataFrame.
    """
    logger.info(f"Requesting historical M15 data for {symbol} from {start_date} to {end_date}...")
    
    # Request bars using the locked TIMEFRAME_M15 constant
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, start_date, end_date)
    
    if rates is None or len(rates) == 0:
        logger.error(f"Failed to retrieve data. Error code: {mt5.last_error()}")
        return pd.DataFrame()
        
    # Convert structured numpy array directly to Pandas DataFrame
    df = pd.DataFrame(rates)
    
    # Convert the unix timestamp integer to a readable datetime format
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    logger.info(f"Successfully downloaded {len(df)} historical M15 bars.")
    return df

def shutdown_mt5_session():
    """Safely closes the connection to the MetaTrader 5 terminal."""
    mt5.shutdown()
    logger.info("MetaTrader 5 session closed safely.")

if __name__ == "__main__":
    # Fixed execution parameters for Phase 2 data extraction
    TARGET_SYMBOL = "XAUUSD"
    START_UTC = datetime(2020, 1, 1)
    END_UTC = datetime(2026, 8, 31)
    
    # Execute structural pipeline sequence
    if initialize_mt5_session():
        try:
            if verify_market_symbol(TARGET_SYMBOL):
                historical_data = fetch_historical_m15_bars(TARGET_SYMBOL, START_UTC, END_UTC)
                
                # Sample validation to prove connection works before local export
                if not historical_data.empty:
                    print("\n--- Data Sample Extracted Successfully ---")
                    print(historical_data.head())
                    print("------------------------------------------\n")
                    
        finally:
            shutdown_mt5_session()

