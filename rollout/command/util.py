

def get_service_name(args, config) -> str:
    if args.service:
        return args.service

    services = config.get('services')
    for name, service in services.items():
        if service.get('default'):
            return name
