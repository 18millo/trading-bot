"""
Strategy Engine - Core logic for processing trading strategies
Based on ICT concepts: Market Structure, Liquidity, Engulfing Candles
Enhanced with Support/Resistance detection from 1H candles and 1min entries
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    BULLISH = "BUY"
    BEARISH = "SELL"

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: object
    
    @property
    def is_bullish(self) -> bool:
        return self.close > self.open
    
    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)
    
    @property
    def range_size(self) -> float:
        return self.high - self.low
    
    @property
    def body_percentage(self) -> float:
        if self.range_size == 0:
            return 0
        return self.body_size / self.range_size

def detect_support_resistance(candles_1h: List[Candle], num_levels: int = 5) -> Tuple[List[float], List[float]]:
    """
    Detect support and resistance levels from 1-hour candles
    Returns: (support_levels, resistance_levels)
    """
    if len(candles_1h) < 20:
        return [], []
    
    # Find swing highs (resistance) and swing lows (support)
    swing_highs = []
    swing_lows = []
    min_swing = 5
    
    for i in range(min_swing, len(candles_1h) - min_swing):
        # Check for swing high (resistance)
        is_swing_high = True
        for j in range(i - min_swing, i + min_swing + 1):
            if j != i and candles_1h[i].high < candles_1h[j].high:
                is_swing_high = False
                break
        if is_swing_high:
            swing_highs.append(candles_1h[i].high)
        
        # Check for swing low (support)
        is_swing_low = True
        for j in range(i - min_swing, i + min_swing + 1):
            if j != i and candles_1h[i].low > candles_1h[j].low:
                is_swing_low = False
                break
        if is_swing_low:
            swing_lows.append(candles_1h[i].low)
    
    # Cluster nearby levels and get top N
    resistance_levels = cluster_levels(swing_highs, num_levels)
    support_levels = cluster_levels(swing_lows, num_levels)
    
    return support_levels, resistance_levels

def cluster_levels(levels: List[float], num_levels: int) -> List[float]:
    """Cluster nearby price levels and return top N"""
    if not levels:
        return []
    
    # Sort levels
    sorted_levels = sorted(levels)
    clustered = []
    current_cluster = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        if level - current_cluster[-1] < 0.001:  # Within 10 pips for EURUSD
            current_cluster.append(level)
        else:
            clustered.append(sum(current_cluster) / len(current_cluster))
            current_cluster = [level]
    
    clustered.append(sum(current_cluster) / len(current_cluster))
    
    # Return most recent/strongest levels
    return sorted(clustered)[-num_levels:] if len(clustered) > num_levels else clustered

def is_near_level(price: float, levels: List[float], threshold: float = 0.0005) -> bool:
    """Check if price is near a support/resistance level"""
    return any(abs(price - level) <= threshold for level in levels)

def detect_market_structure(candles: List[Candle], min_swing: int = 10) -> Optional[Direction]:
    """
    Detect market structure based on HH/HL (bullish) or LH/LL (bearish)
    """
    if len(candles) < min_swing * 2:
        return None
    
    swing_highs = []
    swing_lows = []
    
    for i in range(min_swing, len(candles) - min_swing):
        is_swing_high = True
        for j in range(i - min_swing, i + min_swing + 1):
            if j != i and candles[i].high < candles[j].high:
                is_swing_high = False
                break
        if is_swing_high:
            swing_highs.append(candles[i])
        
        is_swing_low = True
        for j in range(i - min_swing, i + min_swing + 1):
            if j != i and candles[i].low > candles[j].low:
                is_swing_low = False
                break
        if is_swing_low:
            swing_lows.append(candles[i])
    
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return None
    
    recent_highs = swing_highs[-3:]
    recent_lows = swing_lows[-3:]
    
    # Uptrend: Higher Highs and Higher Lows
    uptrend = True
    for i in range(len(recent_highs)-1):
        if recent_highs[i].high >= recent_highs[i+1].high:
            uptrend = False
            break
    
    if uptrend:
        for i in range(len(recent_lows)-1):
            if recent_lows[i].low >= recent_lows[i+1].low:
                uptrend = False
                break
        if uptrend:
            return Direction.BULLISH
    
    # Downtrend: Lower Highs and Lower Lows
    downtrend = True
    for i in range(len(recent_highs)-1):
        if recent_highs[i].high <= recent_highs[i+1].high:
            downtrend = False
            break
    
    if downtrend:
        for i in range(len(recent_lows)-1):
            if recent_lows[i].low <= recent_lows[i+1].low:
                downtrend = False
                break
        if downtrend:
            return Direction.BEARISH
    
    return None

def detect_liquidity_sweep(candles: List[Candle], liquidity_type: str = "previous_high_low") -> Optional[Direction]:
    """
    Detect liquidity sweeps (stop hunts)
    Returns direction to trade AFTER the sweep
    """
    if len(candles) < 20:
        return None
    
    recent = candles[-20:]
    current = candles[-1]
    
    if liquidity_type == "previous_high_low":
        prev_high = max(c.high for c in recent[:-1])
        prev_low = min(c.low for c in recent[:-1])
        
        # Bullish sweep: price took sell-side liquidity (swept lows), then closed above
        if current.low < prev_low and current.close > current.open:
            return Direction.BULLISH
        
        # Bearish sweep: price took buy-side liquidity (swept highs), then closed below
        if current.high > prev_high and current.close < current.open:
            return Direction.BEARISH
    
    return None

def detect_engulfing(candles: List[Candle], min_body_percentage: float = 0.6, require_full_engulf: bool = True) -> Optional[Direction]:
    """
    Detect engulfing candles as entry trigger on 1min timeframe
    """
    if len(candles) < 2:
        return None
    
    prev = candles[-2]
    curr = candles[-1]
    
    # Bullish engulfing: current candle closes above previous high, opens below previous close
    if curr.is_bullish and not prev.is_bullish:  # prev was bearish
        if require_full_engulf:
            if curr.open <= prev.close and curr.close >= prev.open:
                if curr.body_percentage >= min_body_percentage:
                    return Direction.BULLISH
        else:
            if curr.body_size > prev.body_size:
                return Direction.BULLISH
    
    # Bearish engulfing
    if not curr.is_bullish and prev.is_bullish:  # prev was bullish
        if require_full_engulf:
            if curr.open >= prev.close and curr.close <= prev.open:
                if curr.body_percentage >= min_body_percentage:
                    return Direction.BEARISH
        else:
            if curr.body_size > prev.body_size:
                return Direction.BEARISH
    
    return None

def detect_bos(candles: List[Candle], direction: Direction) -> bool:
    """
    Detect Break of Structure (BOS) or Change of Character (CHoCH)
    """
    if len(candles) < 10:
        return False
    
    recent = candles[-10:]
    
    if direction == Direction.BULLISH:
        recent_high = max(c.high for c in recent[:-1])
        return candles[-1].close > recent_high
    else:  # BEARISH
        recent_low = min(c.low for c in recent[:-1])
        return candles[-1].close < recent_low

def evaluate_strategy(candles_1min: List[Candle], candles_1h: List[Candle], config: Dict) -> Optional[Dict]:
    """
    ENB Strategy Evaluation with Support/Resistance (Enhanced)
    Uses 1H candles for S/R levels, 1min candles for entry execution
    
    Returns trade signal if ALL conditions are met:
    1. Market Structure aligns (HH/HL for BUY, LH/LL for SELL)
    2. Liquidity is swept (previous LOW for BUY, previous HIGH for SELL)
    3. Engulfing candle on 1min timeframe
    4. Price is near Support (for BUY) or Resistance (for SELL) from 1H
    5. (Optional) BOS/CHoCH confirmation
    """
    if len(candles_1min) < 20:
        return None
    
    signals = {
        "structure": None,
        "liquidity": None,
        "engulfing": None,
        "bos": None,
        "support_resistance": None
    }
    
    # Detect Support/Resistance from 1H candles
    if config.get("support_resistance", {}).get("enabled", True):
        support_levels, resistance_levels = detect_support_resistance(
            candles_1h,
            num_levels=config.get("support_resistance", {}).get("num_levels", 5)
        )
        
        current_price = candles_1min[-1].close
        threshold = config.get("support_resistance", {}).get("threshold", 0.0005)
        
        # Check if price is near S/R level
        near_support = is_near_level(current_price, support_levels, threshold)
        near_resistance = is_near_level(current_price, resistance_levels, threshold)
        
        signals["support_resistance"] = {
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "near_support": near_support,
            "near_resistance": near_resistance,
            "current_price": current_price
        }
    
    # Step 1: Market Structure (REQUIRED) - Use 1min for structure
    if config.get("structure", {}).get("enabled", True):
        structure = detect_market_structure(
            candles_1min, 
            min_swing=config.get("structure", {}).get("min_swing_strength", 10)
        )
        signals["structure"] = structure
    
    # Step 2: Liquidity Sweep (REQUIRED if enabled)
    liquidity_config = config.get("liquidity", {})
    if liquidity_config.get("enabled", True) and liquidity_config.get("require_sweep", True):
        liquidity = detect_liquidity_sweep(
            candles_1min,
            liquidity_type=liquidity_config.get("type", "previous_high_low")
        )
        signals["liquidity"] = liquidity
    
    # Step 3: Engulfing Confirmation on 1min (REQUIRED if enabled)
    entry_config = config.get("entry", {})
    if entry_config.get("require_engulfing", True):
        engulfing = detect_engulfing(
            candles_1min,
            min_body_percentage=entry_config.get("body_strength_min", 0.6),
            require_full_engulf=entry_config.get("body_engulf_required", True)
        )
        signals["engulfing"] = engulfing
    
    # Step 4: Check Support/Resistance alignment
    sr_config = config.get("support_resistance", {})
    if sr_config.get("enabled", True) and signals["support_resistance"]:
        sr_data = signals["support_resistance"]
        
        # For BUY: need to be near support
        if signals["structure"] == Direction.BULLISH or signals["liquidity"] == Direction.BULLISH:
            if not sr_data["near_support"]:
                return None  # Not near support, skip
        
        # For SELL: need to be near resistance
        if signals["structure"] == Direction.BEARISH or signals["liquidity"] == Direction.BEARISH:
            if not sr_data["near_resistance"]:
                return None  # Not near resistance, skip
    
    # Step 5: BOS/CHoCH (OPTIONAL)
    confirmation = config.get("confirmation", {})
    if confirmation.get("require_bos", False):
        check_direction = signals["structure"] or signals["liquidity"]
        if check_direction:
            signals["bos"] = detect_bos(candles_1min, check_direction)
    
    # ENB STRATEGY: ALL conditions must align
    structure_ok = signals["structure"] is not None
    liquidity_ok = signals["liquidity"] is not None if liquidity_config.get("enabled", True) else True
    engulfing_ok = signals["engulfing"] is not None
    
    if structure_ok and liquidity_ok and engulfing_ok:
        # Check if all directions align
        directions = [s for s in [signals["structure"], signals["liquidity"], signals["engulfing"]] if s is not None]
        if directions and all(d == directions[0] for d in directions):
            # Optional BOS check
            if confirmation.get("require_bos", False) and not signals["bos"]:
                return None
            
            return {
                "signal": directions[0].value,
                "confidence": "HIGH" if signals.get("bos") else "MEDIUM",
                "triggers": signals,
                "support_levels": signals["support_resistance"]["support_levels"] if signals["support_resistance"] else [],
                "resistance_levels": signals["support_resistance"]["resistance_levels"] if signals["support_resistance"] else []
            }
    
    return None
