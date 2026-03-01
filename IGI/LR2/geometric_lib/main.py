import square
import circle
import os

sideSquare = float(os.getenv('SQUARE_SIDE', '5'))
radiusCircle = float(os.getenv('CIRCLE_RADIUS', '3'))

print(f"Square area: {square.area(sideSquare)}")
print(f"Square perimeter: {square.perimeter(sideSquare)}")
print(f"Circle area: {circle.area(radiusCircle)}")
print(f"Circle perimeter: {circle.perimeter(radiusCircle)}")
