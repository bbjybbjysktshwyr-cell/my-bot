local ScreenGui = Instance.new("ScreenGui")
local TextButton = Instance.new("TextButton")

ScreenGui.Parent = game.CoreGui
TextButton.Parent = ScreenGui
TextButton.BackgroundColor3 = Color3.fromRGB(0, 255, 0)
TextButton.Position = UDim2.new(0.4, 0, 0.4, 0)
TextButton.Size = UDim2.new(0, 200, 0, 50)
TextButton.Text = "إذا ظهر هذا الزر فالمنفذ يعمل!"
TextButton.TextSize = 14

TextButton.MouseButton1Click:Connect(function()
    print("تم النقر على الزر بنجاح!")
end)
