defmodule Botschaft.Providers do
  def child_spec([opts]) do
    opts = Keyword.put(opts, :strategy, :one_for_one)

    children =
      for provider <- providers() do
        {provider, [&Botschaft.Config.get_provider_config/1]}
      end

    %{
      id: __MODULE__,
      start: {Supervisor, :start_link, [children, opts]},
      type: :supervisor
    }
  end

  defp providers() do
    [
      Botschaft.Providers.Telegram,
      Botschaft.Providers.Discord,
      Botschaft.Providers.Slack
    ]
  end

  def reload_config() do
    IO.puts("reloading config")
    Botschaft.Config.reload()

    for provider <- providers() do
      provider.reload_config()
    end

    :ok
  end

  def send_message(provider, destination, %Botschaft.Message{} = message)
      when is_binary(destination) do
    pmod = Recase.to_title(provider)
    module = String.to_existing_atom("Elixir.Botschaft.Providers.#{pmod}")
    apply(module, :send, [destination, message])
  end
end
