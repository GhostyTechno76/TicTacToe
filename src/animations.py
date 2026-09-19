"""Small, time-based animation helpers used by the game UI."""


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def lerp(start, end, amount):
    return start + (end - start) * amount


def ease_out_cubic(progress):
    progress = clamp(progress)
    return 1 - (1 - progress) ** 3


def ease_out_back(progress):
    progress = clamp(progress)
    overshoot = 1.70158
    value = progress - 1
    return 1 + (overshoot + 1) * value**3 + overshoot * value**2


def ease_in_out(progress):
    progress = clamp(progress)
    if progress < 0.5:
        return 2 * progress * progress
    return 1 - ((-2 * progress + 2) ** 2) / 2


def approach(current, target, speed, dt):
    """Move a value toward a target at a time-based rate."""
    if current < target:
        return min(target, current + speed * dt)
    return max(target, current - speed * dt)
