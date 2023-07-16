defmodule Botschaft.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Start the Telemetry supervisor
      Botschaft.Telemetry,
      BotschaftWeb.Telemetry,
      # Start the PubSub system
      {Phoenix.PubSub, name: Botschaft.PubSub},
      # Start Finch
      {Finch, name: Botschaft.Finch},
      # Start the Endpoint (http/https)
      BotschaftWeb.Endpoint,
      # Start a worker by calling: Botschaft.Worker.start_link(arg)
      # {Botschaft.Worker, arg}
      Botschaft.Config,
      Botschaft.Providers.child_spec([[name: Botschaft.Providers.Supervisor]]),
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Botschaft.Supervisor]
    # start children
    sup = Supervisor.start_link(children, opts)
    # set config reload handler
    System.trap_signal(:sighup, &Botschaft.Providers.reload_config/0)
    sup
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    BotschaftWeb.Endpoint.config_change(changed, removed)
    :ok
  end

end
