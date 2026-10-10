.PHONY: demo backend frontend

demo:
	@echo "Starting backend and frontend for Demo..."
	@start /B cmd /c "cd backend && python main.py"
	@start /B cmd /c "cd frontend && npm run dev"
	@echo "Demo is running. Access frontend at http://localhost:3000?demo=1"

backend:
	cd backend && python main.py

frontend:
	cd frontend && npm run dev
