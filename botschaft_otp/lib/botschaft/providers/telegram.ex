defmodule Botschaft.Providers.Telegram do
  use Botschaft.Provider, :telegram

  @moduledoc false

  @r "https://api.telegram.org"

  def handle_call({:message, %{destination: name, message: message}}, _from, %{config: %{vars: shared_vars} = config} = state) do
    case Botschaft.Config.ProviderConfig.get_destination_config(config, name) do
      %{"token" => token, "chat_id" => chat_id, "vars" => vars} ->
        vars = Map.merge(shared_vars, vars)
        message = Botschaft.Message.render(message, vars)
        case send_message(message, chat_id, token) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "telegram", destination: name, success: true})
            {:reply, :ok, state}
          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{provider: "telegram", destination: name, success: false})
            {:reply, {:error, reason}, state}
        end
      nil ->
        {:reply, {:error, "No telegram destination #{name}"}, state}
    end
  end

  defp send_message(text, chat_id, bot_token) do
    url = url_for_bot(bot_token)
    # https://core.telegram.org/bots/api#sendmessage
    resp = Botschaft.Http.Client.get(url, [chat_id: chat_id, text: text])
    if resp.status != 200 do
      {:error, "Failed to send message: #{inspect resp}"}
    else
      :ok
    end
  end

  defp url_for_bot(bot_token) do
    path = "/bot#{bot_token}/sendMessage"
    @r <> path
  end

end
