# Makefile for CUA Sandbox Operations

.PHONY: reset

reset:
	@echo "🧹 Wiping the Sandbox clean..."
	rm -rf projects/*
	@echo "📦 Restoring the pristine calculator template..."
	cp -r templates/calculator projects/
	@echo "✅ Sandbox reset is complete! Ready for the next Chaos Injection!"