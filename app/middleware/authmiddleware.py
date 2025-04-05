from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.auth import verify_token  # Import your token verification function

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the actual root path from the request
        root_path = request.scope.get("root_path", "")
        # Exclude docs and OpenAPI paths
        if request.url.path.startswith((f"{root_path}/docs", f"{root_path}/redoc", f"{root_path}/openapi.json")):
            return await call_next(request)
        
        # Allow unauthenticated routes
        public_routes = ["/auth/login", "/auth/refresh",'/onboardusers/','/users/','/docs','/favicon.ico','/','/users/verify'
                         ,"/data/departments",'/data/roles']
        print(request.url.path,'requesturl')
        if request.url.path in public_routes:
            return await call_next(request)

        # Get Authorization header

        auth_header = request.headers.get("Authorization")
    
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )

        # Extract token
        token = auth_header.split(" ")[1]
       
        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Add user info to request state
        request.state.user = payload["sub"]

        return await call_next(request)
