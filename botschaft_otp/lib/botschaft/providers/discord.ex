defmodule Botschaft.Providers.Discord do
  use Botschaft.Provider, :discord

  def handle_call({:message, %{destination: name, message: message}}, _from, %{config: %{vars: shared_vars} = config} = state) do
    case Botschaft.Config.ProviderConfig.get_destination_config(config, name) do
      %{"webhook_url" => webhook_url, "vars" => destination_vars} ->
        vars = Map.merge(shared_vars, destination_vars)
        message = Botschaft.Message.render(message, vars)
        case send_message(webhook_url, message) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "discord", destination: name, success: true})
            {:reply, :ok, state}
          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "discord", destination: name, success: false})
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No discord destination #{name}"}, state}
    end
  end

  defp send_message(webhook_url, text) do
    IO.puts "sending message to discord: #{text} @ #{webhook_url}"
    body = %{content: text}
    # https://discord.com/developers/docs/resources/webhook#execute-webhook
    resp = Botschaft.Http.Client.post(webhook_url, body, [wait: "true"])
    if resp.status != 200 do
      {:error, "Failed to send message: #{inspect resp}"}
    else
      :ok
    end
  end

end
