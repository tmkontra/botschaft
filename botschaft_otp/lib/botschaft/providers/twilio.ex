defmodule Botschaft.Providers.Twilio do
  use Botschaft.Provider, :twilio

  def handle_call(
        {:message, %{destination: name, message: message}},
        _from,
        %{config: %{vars: shared_vars} = config} = state
      ) do
    case Botschaft.Config.ProviderConfig.get_destination_config(config, name) do
      %{"account_sid" => sid, "auth_token" => token, "from" => from_number, "to" => to_number, "vars" => destination_vars} ->
        vars = Map.merge(shared_vars, destination_vars)
        message = Botschaft.Message.render(message, vars)

        case send_message(sid, token, from_number, to_number, message) do
          :ok ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{
              provider: "twilio",
              destination: name,
              success: true
            })

            {:reply, :ok, state}

          {:error, reason} ->
            :telemetry.execute([:botschaft, :message, :sent], %{}, %{
              provider: "twilio",
              destination: name,
              success: false
            })

            {:reply, {:error, reason}, state}
        end

      nil ->
        {:reply, {:error, "No discord destination #{name}"}, state}
    end
  end

  defp send_message(sid, token, from_number, to_number, message) do
    # https://www.twilio.com/docs/sms/api/message-resource#create-a-message-resource
    webhook_url = "https://api.twilio.com/2010-04-01/Accounts/#{sid}/Messages.json"
    IO.puts("sending message to twilio @ #{webhook_url}")
    form = %{
      From: from_number,
      Body: message,
      To: to_number,
    }
    resp = Botschaft.Http.Client.post(webhook_url, auth: {sid, token}, form: form)

    if resp.status != 200 do
      {:error, "Failed to send message: #{inspect(resp)}"}
    else
      :ok
    end
  end
end
