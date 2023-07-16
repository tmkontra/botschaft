defmodule Botschaft.Providers do
  def child_spec([opts]) do
    opts = Keyword.put(opts, :strategy, :one_for_one)
    children = for provider <- providers() do
      {provider, [&Botschaft.Config.get_provider/1]}
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
    ]
  end

  def reload_config() do
    IO.puts "reloading config"
    Botschaft.Config.reload()
    for provider <- providers() do
      provider.reload_config()
    end
    :ok
  end

  def send_message(provider, destination, message_text) when is_binary(provider) and is_binary(destination) and is_binary(message_text) do
    pmod = Recase.to_title(provider)
    module = String.to_existing_atom("Elixir.Botschaft.Providers.#{pmod}")
    apply(module, :send, [destination, message_text])
  end
end
